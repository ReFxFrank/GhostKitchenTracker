import pytest

from snapshots import Snapshot, SnapshotError


def test_write_finalize_read_roundtrip(tmp_path):
    snap = Snapshot("testsrc", "2026-08-05", root=tmp_path)
    snap.write_page(0, [{"a": "1"}, {"a": "2"}])
    snap.write_page(1, [{"a": "3", "b": "x"}])
    snap.finalize({"rows": 3})

    rows = list(snap.iter_rows())
    assert len(rows) == 3
    frame = snap.read_frame()
    assert len(frame) == 3
    assert set(frame.columns) == {"a", "b"}


def test_completed_snapshot_is_immutable(tmp_path):
    snap = Snapshot("testsrc", "2026-08-05", root=tmp_path)
    snap.write_page(0, [{"a": "1"}])
    snap.finalize({"rows": 1})
    with pytest.raises(SnapshotError):
        snap.write_page(1, [{"a": "2"}])
    with pytest.raises(SnapshotError):
        snap.finalize({"rows": 2})


def test_reading_incomplete_snapshot_refuses(tmp_path):
    snap = Snapshot("testsrc", "2026-08-05", root=tmp_path)
    snap.write_page(0, [{"a": "1"}])
    with pytest.raises(SnapshotError):
        list(snap.iter_rows())


def test_latest_complete_skips_unfinished(tmp_path):
    old = Snapshot("testsrc", "2026-08-01", root=tmp_path)
    old.write_page(0, [{"a": "1"}])
    old.finalize({"rows": 1})
    newer_unfinished = Snapshot("testsrc", "2026-08-05", root=tmp_path)
    newer_unfinished.write_page(0, [{"a": "2"}])

    latest = Snapshot.latest_complete("testsrc", root=tmp_path)
    assert latest.date == "2026-08-01"


def test_latest_complete_errors_when_nothing_exists(tmp_path):
    with pytest.raises(SnapshotError):
        Snapshot.latest_complete("nope", root=tmp_path)
