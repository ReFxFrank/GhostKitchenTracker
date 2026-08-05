"""Postgres access + schema application.

Applies the Drizzle-generated migration (packages/schema/drizzle/0000_init.sql)
and the trigger/constraint invariants (packages/schema/sql/invariants.sql).
Requires the dockerized Postgres+PostGIS from ops/docker-compose.yml.
"""

from __future__ import annotations

from pathlib import Path

import psycopg

import config

DRIZZLE_BREAKPOINT = "--> statement-breakpoint"


def connect() -> psycopg.Connection:
    return psycopg.connect(config.DATABASE_URL)


def _split_drizzle_sql(text: str) -> list[str]:
    return [s.strip() for s in text.split(DRIZZLE_BREAKPOINT) if s.strip()]


def _tables_exist(conn: psycopg.Connection) -> bool:
    row = conn.execute(
        "SELECT to_regclass('public.buildings') IS NOT NULL"
    ).fetchone()
    return bool(row and row[0])


def init_db(
    schema_sql: Path | None = None,
    invariants_sql: Path | None = None,
) -> dict[str, bool]:
    """Idempotent: skips the base migration when tables already exist; the
    invariants file is written to be re-runnable and is always applied."""
    schema_path = schema_sql or config.SCHEMA_SQL
    invariants_path = invariants_sql or config.INVARIANTS_SQL
    applied = {"schema": False, "invariants": False}
    with connect() as conn:
        if not _tables_exist(conn):
            for stmt in _split_drizzle_sql(schema_path.read_text()):
                conn.execute(stmt)
            applied["schema"] = True
        conn.execute(invariants_path.read_text())
        applied["invariants"] = True
        conn.commit()
    return applied
