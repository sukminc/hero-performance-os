export default function AppHomePage() {
  return (
    <>
      <section className="page-card">
        <p className="eyebrow">Dashboard</p>
        <h1>Authenticated app shell is ready.</h1>
        <p className="subtle">
          This page is the Phase 1 protected-shell target. Phase 2 will wire upload history and processing status here.
        </p>
      </section>
      <section className="grid two">
        <article className="page-card">
          <h3>What exists now</h3>
          <p className="subtle">Route protection, nav structure, Supabase auth scaffolding, and operator gating foundation.</p>
        </article>
        <article className="page-card">
          <h3>What comes next</h3>
          <p className="subtle">Upload packet flow, ownership, job status, and user-facing Today / Review / Brain surfaces.</p>
        </article>
      </section>
    </>
  );
}
