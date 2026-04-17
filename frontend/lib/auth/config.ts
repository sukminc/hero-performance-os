export const AUTH_PROVIDER = "supabase-auth";

export const PUBLIC_ROUTES = ["/", "/login", "/signup", "/pricing"] as const;

export const APP_NAV = [
  { href: "/app", label: "Dashboard" },
  { href: "/app/upload", label: "Upload" },
  { href: "/app/today", label: "Today" },
  { href: "/app/review", label: "Review" },
  { href: "/app/brain", label: "Brain" },
  { href: "/app/account", label: "Account" }
];
