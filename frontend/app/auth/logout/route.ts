import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const response = NextResponse.redirect(new URL("/", request.url));
  response.cookies.set("sb-auth-token", "", { expires: new Date(0), path: "/" });
  return response;
}
