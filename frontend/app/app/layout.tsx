import Link from "next/link";
import { cookies } from "next/headers";
import { APP_NAV } from "@/lib/auth/config";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies();
  const role = cookieStore.get("opb_role")?.value || "user";

  return (
    <main className="shell app-layout">
      <aside className="nav-card">
        <p className="eyebrow">Authenticated App</p>
        <h2>One Percent Better</h2>
        <p className="subtle">
          {role === "operator"
            ? "Operator/admin view is active. You can inspect the public shell and jump into operator-only space."
            : "Public MVP shell for authenticated users. Operator-only routes remain separate."}
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
