import Link from "next/link";
import { APP_NAV } from "@/lib/auth/config";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="shell app-layout">
      <aside className="nav-card">
        <p className="eyebrow">Authenticated App</p>
        <h2>One Percent Better</h2>
        <p className="subtle">Public MVP shell for authenticated users. Operator-only routes remain separate.</p>
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
