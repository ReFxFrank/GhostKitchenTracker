"""SEANCE ingest CLI.

Every stage is runnable standalone. Later-phase stages remain loud stubs.

Raw snapshots are immutable: every fetch writes a dated, compressed file to
data/raw/{source}/{YYYY-MM-DD}/ and is never mutated. All downstream stages
read snapshots, never live sources.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(
    name="seance",
    help="SEANCE ingest: fetch, normalize, classify, link. NYC only, by design.",
    no_args_is_help=True,
)


def _stub(stage: str, phase: str) -> None:
    typer.secho(
        f"{stage}: not implemented — this is {phase} work.",
        fg=typer.colors.YELLOW,
        err=True,
    )
    raise typer.Exit(code=2)


def _done(snap) -> None:
    m = snap.manifest()
    partial = " (PARTIAL — smoke test, not a real snapshot)" if m.get("partial") else ""
    typer.secho(
        f"snapshot complete: {snap.dir} — {m.get('rows', '?')} rows{partial}",
        fg=typer.colors.GREEN,
    )


# ---------------------------------------------------------------------------
# Phase 1 — fetch
# ---------------------------------------------------------------------------


@app.command()
def fetch_dohmh(
    page_size: int = typer.Option(10_000, help="Socrata $limit per request"),
    max_pages: Optional[int] = typer.Option(None, help="Stop early (marks snapshot partial)"),
) -> None:
    """Fetch DOHMH inspections (Socrata 43nn-pn8j) into a dated raw snapshot."""
    from sources import dohmh

    _done(dohmh.fetch(page_size=page_size, max_pages=max_pages))


@app.command()
def fetch_pluto(
    page_size: int = typer.Option(10_000),
    max_pages: Optional[int] = typer.Option(None),
) -> None:
    """Fetch PLUTO attributes (Socrata 64uk-42ks) into a dated raw snapshot."""
    from sources import pluto

    _done(pluto.fetch(page_size=page_size, max_pages=max_pages))


@app.command()
def fetch_dcwp(
    page_size: int = typer.Option(10_000),
    max_pages: Optional[int] = typer.Option(None),
) -> None:
    """Fetch DCWP Issued Licenses (Socrata w7w3-xahh) into a dated raw snapshot."""
    from sources import dcwp

    _done(dcwp.fetch(page_size=page_size, max_pages=max_pages))


@app.command()
def fetch_overture(
    limit: Optional[int] = typer.Option(
        None, help="Row cap for smoke tests (marks snapshot partial)"
    ),
) -> None:
    """Pull the NYC bbox from the pinned Overture places release via DuckDB."""
    from sources import overture

    _done(overture.fetch(limit=limit))


@app.command()
def fetch_fsq(
    limit: Optional[int] = typer.Option(
        None, help="Row cap for smoke tests (marks snapshot partial)"
    ),
) -> None:
    """Pull the NYC bbox from Foursquare OS Places (coverage supplement).

    Gated distribution — requires HF_TOKEN; see sources/fsq.py."""
    from sources import fsq

    _done(fsq.fetch(limit=limit))


# ---------------------------------------------------------------------------
# Phase 1 — normalize / load / coverage
# ---------------------------------------------------------------------------


@app.command()
def normalize(
    date: Optional[str] = typer.Option(None, help="Snapshot date (default: latest complete)"),
) -> None:
    """Dedupe violations to inspection level; canonicalize names and phones.

    Writes staging parquet to data/staging/{date}/."""
    import config
    from normalize import inspections as norm
    from snapshots import Snapshot

    import json

    snap = Snapshot("dohmh", date) if date else Snapshot.latest_complete("dohmh")
    partial = bool(snap.manifest().get("partial"))
    if partial:
        typer.secho(
            "WARNING: normalizing a PARTIAL snapshot — smoke-test output only; "
            "the staging manifest is marked partial and `load` will refuse it",
            fg=typer.colors.YELLOW,
        )
    frames = norm.normalize_snapshot(snap.read_frame())
    out = config.STAGING_DIR / snap.date
    out.mkdir(parents=True, exist_ok=True)
    rows = {}
    for name, frame in frames.items():
        frame.write_parquet(out / f"{name}.parquet")
        rows[name] = len(frame)
        typer.echo(f"{name}: {len(frame)} rows -> {out / (name + '.parquet')}")

    try:
        psnap = Snapshot("pluto", date) if date else Snapshot.latest_complete("pluto")
        partial = partial or bool(psnap.manifest().get("partial"))
        pluto_df = norm.pluto_frame(psnap.read_frame())
        pluto_df.write_parquet(out / "pluto.parquet")
        rows["pluto"] = len(pluto_df)
        typer.echo(f"pluto: {len(pluto_df)} rows -> {out / 'pluto.parquet'}")
    except Exception as exc:  # no pluto snapshot yet is fine; anything else is not
        from snapshots import SnapshotError

        if isinstance(exc, SnapshotError):
            typer.secho(f"pluto: skipped ({exc})", fg=typer.colors.YELLOW)
        else:
            raise

    # The staging manifest is how `load` knows this staging is safe to load.
    (out / "staging_manifest.json").write_text(
        json.dumps(
            {"source_date": snap.date, "partial": partial, "rows": rows}, indent=2
        )
    )


@app.command()
def init_db() -> None:
    """Apply the Drizzle migration + DB invariants (triggers, checks). Idempotent."""
    import db

    applied = db.init_db()
    typer.echo(f"schema applied: {applied['schema']}; invariants applied: {applied['invariants']}")


@app.command()
def load(
    date: Optional[str] = typer.Option(None, help="Staging date to load (default: latest overture/dohmh)"),
    with_places: bool = typer.Option(True, help="Also load the Overture places snapshot"),
    allow_partial: bool = typer.Option(
        False, help="Load partial/smoke-test staging anyway (dev only; never in cron)"
    ),
) -> None:
    """Load staging parquet into Postgres (upserts; inspections replace-all)."""
    import json

    import config
    from snapshots import Snapshot, SnapshotError

    dohmh_snap = Snapshot("dohmh", date) if date else Snapshot.latest_complete("dohmh")

    staging_manifest = config.STAGING_DIR / dohmh_snap.date / "staging_manifest.json"
    if not staging_manifest.exists():
        typer.secho(
            f"no staging manifest at {staging_manifest} — run `normalize` (again) "
            "for this date; refusing to load unmarked staging",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)
    if json.loads(staging_manifest.read_text()).get("partial") and not allow_partial:
        typer.secho(
            "staging is marked PARTIAL (smoke test). Refusing to load it into the "
            "database — the inspections/violations tables are replace-all and this "
            "would wipe real data. Use --allow-partial only in a dev database.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    # DB-dependent imports happen only after the guards pass, so a refusal
    # never depends on psycopg being installed.
    import load as loader
    from sources import overture as ov

    overture_parquet = None
    release = None
    if with_places:
        try:
            osnap = Snapshot.latest_complete("overture", include_partial=allow_partial)
            overture_parquet = ov.parquet_path(osnap)
            release = osnap.manifest().get("release")
        except SnapshotError:
            typer.secho("no overture snapshot; loading without places", fg=typer.colors.YELLOW)
    counts = loader.load_all(dohmh_snap.date, overture_parquet, release)
    for table, n in counts.items():
        typer.echo(f"{table}: {n} rows")


@app.command()
def coverage(
    places_parquet: Optional[Path] = typer.Option(
        None, help="Path to a places parquet (default: latest overture snapshot)"
    ),
    threshold: float = typer.Option(90.0, help="Fuzzy match cutoff (token_set_ratio)"),
) -> None:
    """THE KILL TEST: fraction of seeded known virtual brands present in places."""
    from discovery import coverage as cov
    from snapshots import Snapshot
    from sources import overture as ov

    if places_parquet is not None:
        paths = [places_parquet]
    else:
        from snapshots import SnapshotError

        # latest_complete skips PARTIAL (smoke-test) snapshots by default,
        # so the gate can only ever run against real extracts.
        snap = Snapshot.latest_complete("overture")
        paths = [ov.parquet_path(snap)]
        try:  # include the FSQ supplement automatically once it has been fetched
            from sources import fsq as fsq_mod

            fsnap = Snapshot.latest_complete("fsq")
            paths.append(fsq_mod.parquet_path(fsnap))
        except SnapshotError:
            pass

    report = cov.run(paths)
    typer.echo(f"places: {[str(p) for p in paths]}")
    if report["unsourced_brands"]:
        typer.secho(
            f"NOTE: {len(report['unsourced_brands'])} brand file(s) without sources "
            f"(count toward the gate, fix before trusting it): {report['unsourced_brands']}",
            fg=typer.colors.YELLOW,
        )
    typer.echo("")
    for r in report["results"]:
        mark = "HIT " if r.hit else "MISS"
        typer.echo(f"[{mark}] {r.entry.brand}")
        for name, score, category in r.matches[:3]:
            typer.echo(f"        {score:5.1f}  {name}  ({category})")
    typer.echo("")
    typer.secho(
        f"coverage: {report['hits']}/{report['total_brands']} = {report['pct']:.1f}%",
        fg=typer.colors.CYAN,
        bold=True,
    )
    typer.secho(report["verdict"], bold=True)
    if report["pct"] < 30:
        raise typer.Exit(code=3)


# ---------------------------------------------------------------------------
# Later phases — loud stubs
# ---------------------------------------------------------------------------


@app.command()
def classify() -> None:
    """Venue classifier: facility / food court / single kitchen / institutional. [Phase 2]"""
    _stub("classify", "Phase 2")


@app.command()
def gaps() -> None:
    """Name-gap discovery: ranked candidate ghost brands with host building. [Phase 2]"""
    _stub("gaps", "Phase 2")


@app.command()
def link() -> None:
    """Linkage engine: families, max-per-family scoring, evidence rows. [Phase 3]"""
    _stub("link", "Phase 3")


if __name__ == "__main__":
    app()
