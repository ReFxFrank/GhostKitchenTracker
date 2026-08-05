"""SEANCE ingest CLI.

Every stage is runnable standalone. Stages that belong to a later phase exist
as loud stubs: they name their phase and exit non-zero rather than pretending.

Raw snapshots are immutable: every fetch writes a dated, compressed file to
data/raw/{source}/{YYYY-MM-DD}/ and is never mutated. All downstream stages
read snapshots, never live sources.
"""

from __future__ import annotations

import typer

app = typer.Typer(
    name="seance",
    help="SEANCE ingest: fetch, normalize, classify, link. NYC only, by design.",
    no_args_is_help=True,
)


def _stub(stage: str, phase: str) -> None:
    typer.secho(
        f"{stage}: not implemented — this is {phase} work. "
        "Phase 0 delivers scaffold and legal posture only.",
        fg=typer.colors.YELLOW,
        err=True,
    )
    raise typer.Exit(code=2)


@app.command()
def fetch_dohmh() -> None:
    """Fetch DOHMH inspections (Socrata 43nn-pn8j) into a dated raw snapshot. [Phase 1]"""
    _stub("fetch-dohmh", "Phase 1")


@app.command()
def fetch_pluto() -> None:
    """Fetch PLUTO (Socrata 64uk-42ks) into a dated raw snapshot. [Phase 1]"""
    _stub("fetch-pluto", "Phase 1")


@app.command()
def fetch_overture() -> None:
    """Pull the NYC bbox from the pinned Overture places release via DuckDB. [Phase 1]"""
    _stub("fetch-overture", "Phase 1")


@app.command()
def fetch_dcwp() -> None:
    """Fetch DCWP Issued Licenses (Socrata w7w3-xahh) into a dated raw snapshot. [Phase 1]"""
    _stub("fetch-dcwp", "Phase 1")


@app.command()
def normalize() -> None:
    """Dedupe violations to inspection level; canonicalize names, phones, addresses. [Phase 1]"""
    _stub("normalize", "Phase 1")


@app.command()
def coverage() -> None:
    """THE KILL TEST: fraction of seeded known virtual brands present in places. [Phase 1]"""
    _stub("coverage", "Phase 1")


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
