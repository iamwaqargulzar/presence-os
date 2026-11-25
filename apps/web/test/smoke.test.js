// Starts the built app and checks the placeholder page, request-ID and traceparent headers. Run `pnpm build` first.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { after, before, test } from "node:test";

// Override with PRESENCE_SMOKE_PORT when parallel worktrees run the smoke test at once.
const PORT = Number(process.env.PRESENCE_SMOKE_PORT ?? 3199);
let server;

before(async () => {
  server = spawn(
    "pnpm",
    ["exec", "next", "start", "--hostname", "127.0.0.1", "--port", `${PORT}`],
    {
      stdio: "ignore",
    },
  );
  for (let i = 0; i < 50; i++) {
    try {
      await fetch(`http://127.0.0.1:${PORT}/`);
      return;
    } catch {
      await new Promise((r) => setTimeout(r, 200));
    }
  }
  throw new Error("web app did not start");
});

after(() => server.kill());

test("placeholder page responds with a request ID", async () => {
  const res = await fetch(`http://127.0.0.1:${PORT}/`);
  assert.equal(res.status, 200);
  assert.match(await res.text(), /Presence OS/);
  assert.match(res.headers.get("x-request-id") ?? "", /^[0-9a-f]{32}$/);
});

test("unsafe incoming request ID is replaced", async () => {
  const res = await fetch(`http://127.0.0.1:${PORT}/`, {
    headers: { "x-request-id": "bad id {}" },
  });
  assert.match(res.headers.get("x-request-id") ?? "", /^[0-9a-f]{32}$/);
});

test("a valid incoming trace is continued and an invalid one replaced", async () => {
  const trace = "4bf92f3577b34da6a3ce929d0e0e4736";
  const kept = await fetch(`http://127.0.0.1:${PORT}/`, {
    headers: { traceparent: `00-${trace}-00f067aa0ba902b7-01` },
  });
  assert.match(kept.headers.get("traceparent") ?? "", new RegExp(`^00-${trace}-[0-9a-f]{16}-01$`));
  const replaced = await fetch(`http://127.0.0.1:${PORT}/`, {
    headers: { traceparent: `00-${"0".repeat(32)}-00f067aa0ba902b7-01` },
  });
  const header = replaced.headers.get("traceparent") ?? "";
  assert.match(header, /^00-[0-9a-f]{32}-[0-9a-f]{16}-01$/);
  assert.notEqual(header.slice(3, 35), "0".repeat(32));
});
