export default function AttributionPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-24">
      <h1 className="text-2xl font-semibold tracking-tight">Data attribution</h1>
      <p className="mt-4 text-neutral-600">
        This site is built on open data: NYC Open Data (DOHMH, DCP, DCWP),
        Overture Maps Foundation places (CDLA Permissive 2.0 / Apache 2.0), and
        an OpenStreetMap-derived basemap (ODbL, © OpenStreetMap contributors).
        The generated per-record attribution page ships in Phase 4; the standing
        obligations are documented in{" "}
        <code className="text-sm">docs/ATTRIBUTION.md</code>.
      </p>
    </div>
  );
}
