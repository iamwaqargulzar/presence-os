import { type NextRequest, NextResponse } from "next/server";

// Incoming IDs are untrusted: accept only short plain tokens so they cannot forge log lines.
const SAFE_ID = /^[A-Za-z0-9._-]{1,64}$/;

export function proxy(request: NextRequest) {
  const incoming = request.headers.get("x-request-id") ?? "";
  const requestId = SAFE_ID.test(incoming) ? incoming : crypto.randomUUID().replaceAll("-", "");
  const headers = new Headers(request.headers);
  headers.set("x-request-id", requestId);
  const response = NextResponse.next({ request: { headers } });
  response.headers.set("x-request-id", requestId);
  console.log(
    JSON.stringify({
      ts: new Date().toISOString(),
      level: "INFO",
      logger: "presence.web.request",
      msg: "request",
      request_id: requestId,
      method: request.method,
      path: request.nextUrl.pathname,
    }),
  );
  return response;
}

export const config = { matcher: "/((?!_next/static|_next/image|favicon.ico).*)" };
