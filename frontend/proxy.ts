import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const PUBLIC_PATHS = ["/", "/login", "/signup", "/pricing"];
const APP_PREFIX = "/app";
const OPERATOR_PREFIX = "/operator";
const OPERATOR_ROLE_COOKIE = "opb_role";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isPublicPath = PUBLIC_PATHS.includes(pathname);
  const hasSession = request.cookies.has("sb-access-token") || request.cookies.has("sb-auth-token");
  const operatorRole = request.cookies.get(OPERATOR_ROLE_COOKIE)?.value;

  if (isPublicPath) {
    return NextResponse.next();
  }

  if (pathname.startsWith(APP_PREFIX) && !hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (pathname.startsWith(OPERATOR_PREFIX) && operatorRole !== "operator") {
    return NextResponse.redirect(new URL("/app", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
