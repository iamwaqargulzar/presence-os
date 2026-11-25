import { type NextRequest, NextResponse } from "next/server";

// Incoming IDs are untrusted: accept only short plain tokens so they cannot forge log lines.
const SAFE_ID = /^[A-Za-z0-9._-]{1,64}$/;
// W3C Trace Context (version-traceid-parentid-flags); all-zero IDs are invalid.
const TRACEPARENT = /^00-([0-9a-f]{32})-([0-9a-f]{16})-[0-9a-f]{2}$/;

function hex(bytes: number): string {
  return Array.from(crypto.getRandomValues(new Uint8Array(bytes)), (b) =>
    b.toString(16).padStart(2, "0"),
  ).join("");
}

function traceId(traceparent: string): string {
  const [, trace = "", parent = ""] = TRACEPARENT.exec(traceparent) ?? [];
  return trace && !/^0+$/.test(trace) && !/^0+$/.test(parent) ? trace : hex(16);
}

export function proxy(request: NextRequest) {
  const incoming = request.headers.get("x-request-id") ?? "";
  const requestId = SAFE_ID.test(incoming) ? incoming : crypto.randomUUID().replaceAll("-", "");
  const trace = traceId(request.headers.get("traceparent") ?? "");
  // shortcut: no span export yet; each hop gets a fresh parent ID so the core can join the trace.
  const traceparent = `00-${trace}-${hex(8)}-01`;
  const headers = new Headers(request.headers);
  headers.set("x-request-id", requestId);
  headers.set("traceparent", traceparent);
  const response = NextResponse.next({ request: { headers } });
  response.headers.set("x-request-id", requestId);
  response.headers.set("traceparent", traceparent);
  console.log(
    JSON.stringify({
      ts: new Date().toISOString(),
      level: "INFO",
      logger: "presence.web.request",
      msg: "request",
      request_id: requestId,
      trace_id: trace,
      method: request.method,
      path: request.nextUrl.pathname,
    }),
  );
  return response;
}

export const config = { matcher: "/((?!_next/static|_next/image|favicon.ico).*)" };
