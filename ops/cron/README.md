# Cron

Weekly refresh jobs land here in Phase 6 (definition of done: "NYC-wide dataset,
refreshed weekly by cron, fully reproducible from pinned `data/raw/` snapshots").

Nothing runs on a schedule before there is something correct to run. Each job
will be a thin wrapper over `services/ingest/cli.py` stages, writing a dated
snapshot first and failing loudly on any schema drift — no defensive
`.get(col, '')` quietly producing empty datasets.
