"""Resume must never weld two different fetches into one snapshot, and a
partial smoke-test snapshot must never block-or-masquerade as a real one.
These paths are disk-only (validated before any network I/O)."""

import json

import pytest

from snapshots import Snapshot, SnapshotError
from sources.socrata import fetch_to_snapshot


def _started_snapshot(tmp_path, params: dict) -> Snapshot:
    snap = Snapshot("dohmh", "2026-08-05", root=tmp_path)
    snap.write_page(0, [{"camis": "1"}])
    (snap.dir / "fetch_params.json").write_text(json.dumps(params))
    return snap


def test_resume_with_different_params_refused(tmp_path):
    snap = _started_snapshot(
        tmp_path,
        {"dataset_id": "43nn-pn8j", "select": None, "where": "boro='Queens'",
         "page_size": 10000, "order": ":id"},
    )
    with pytest.raises(SnapshotError, match="resume refused"):
        fetch_to_snapshot(
            dataset_id="43nn-pn8j",
            source_name="dohmh",
            expected_fields={"camis"},
            snapshot=snap,
        )


def test_resume_without_params_file_refused(tmp_path):
    snap = Snapshot("dohmh", "2026-08-05", root=tmp_path)
    snap.write_page(0, [{"camis": "1"}])
    with pytest.raises(SnapshotError, match="fetch_params"):
        fetch_to_snapshot(
            dataset_id="43nn-pn8j",
            source_name="dohmh",
            expected_fields={"camis"},
            snapshot=snap,
        )


def test_resume_stale_started_at_refused(tmp_path):
    import datetime as dt

    old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=2)).isoformat()
    snap = _started_snapshot(
        tmp_path,
        {"dataset_id": "43nn-pn8j", "select": None, "where": None,
         "page_size": 10000, "order": ":id", "started_at": old},
    )
    with pytest.raises(SnapshotError, match="old"):
        fetch_to_snapshot(
            dataset_id="43nn-pn8j",
            source_name="dohmh",
            expected_fields={"camis"},
            snapshot=snap,
        )


def test_resume_unstamped_params_refused(tmp_path):
    snap = _started_snapshot(
        tmp_path,
        {"dataset_id": "43nn-pn8j", "select": None, "where": None,
         "page_size": 10000, "order": ":id"},
    )
    with pytest.raises(SnapshotError, match="unstamped"):
        fetch_to_snapshot(
            dataset_id="43nn-pn8j",
            source_name="dohmh",
            expected_fields={"camis"},
            snapshot=snap,
        )


def test_partial_snapshot_blocks_real_fetch_with_clear_error(tmp_path):
    snap = Snapshot("dohmh", "2026-08-05", root=tmp_path)
    snap.write_page(0, [{"camis": "1"}])
    snap.finalize({"rows": 1, "partial": True})
    with pytest.raises(SnapshotError, match="PARTIAL smoke-test"):
        fetch_to_snapshot(
            dataset_id="43nn-pn8j",
            source_name="dohmh",
            expected_fields={"camis"},
            snapshot=snap,
        )
