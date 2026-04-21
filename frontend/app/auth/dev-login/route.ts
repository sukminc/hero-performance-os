import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  if (process.env.OPB_ENABLE_DEV_LOGIN !== "1") {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  const url = new URL(request.url);
  const role = url.searchParams.get("role") === "operator" ? "operator" : "user";
  const next = url.searchParams.get("next") || (role === "operator" ? "/operator" : "/app");
  const response = NextResponse.redirect(new URL(next, request.url));

  response.cookies.set("sb-auth-token", `dev-${role}-session`, {
    httpOnly: true,
    sameSite: "lax",
    path: "/"
  });

  response.cookies.set("opb_role", role, {
    httpOnly: true,
    sameSite: "lax",
    path: "/"
  });

  return response;
}
