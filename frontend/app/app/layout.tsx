import Link from "next/link";
import { APP_NAV } from "@/lib/auth/config";
import { getViewerContext } from "@/lib/viewer/session";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const viewer = await getViewerContext();
  const role = viewer.role;

  return (
    <main className="shell app-layout">
      <aside className="nav-card">
        <p className="eyebrow">Your Poker Baseline</p>
        <h2>One Percent Better</h2>
        <p className="subtle">
          {role === "operator"
            ? "Operator/admin view is active. The public product now starts from the Matrix experience."
            : "Upload hand histories, then start from your Matrix: how you played, what happened, and what to review."}
        </p>
        <div className="pill-row">
          <span className="pill">{role === "operator" ? "Operator/Admin" : "Standard User"}</span>
          <Link className="pill" href="/auth/logout">
            Logout
          </Link>
          {role === "operator" ? (
            <Link className="pill" href="/operator">
              Operator View
            </Link>
          ) : null}
        </div>
        <nav className="app-nav">
          {APP_NAV.map((item) => (
            <Link key={item.href} href={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <section className="grid">{children}</section>
    </main>
  );
}
