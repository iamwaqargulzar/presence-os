// Starts the built app and checks the placeholder page and request-ID header. Run `pnpm build` first.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { after, before, test } from "node:test";

const PORT = 3199;
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
