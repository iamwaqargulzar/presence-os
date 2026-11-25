#!/usr/bin/env bash
# R0-009 acceptance checks. Run on the VM named by the role, or on a host outside the LAN for `internet`.
# Prints PASS/FAIL per check and exits non-zero on any FAIL. Paste the output into evidence/R0/R0-009/.
#   verify.sh worker     # on the Worker VM: everything private is unreachable
#   verify.sh core       # on the Core VM: data and (if running) inference reachable
#   verify.sh internet   # off-site (e.g. phone hotspot): only the tunnel hostnames answer
# Environment: LAN_PROXMOX (host LAN IP), LAN_ROUTER, INFERENCE (default inference.presence.internal),
#   TEST_HOST, CONSOLE_HOST, WAN_IP (public address of the site), INFERENCE_OFF=1 when host B is powered off.
set -uo pipefail
fail=0
open() { timeout 3 bash -c "exec 3<>/dev/tcp/$1/$2" 2>/dev/null; }
expect_open()   { if open "$1" "$2"; then echo "PASS open   $1:$2"; else echo "FAIL closed $1:$2 (expected open)"; fail=1; fi; }
expect_closed() { if open "$1" "$2"; then echo "FAIL open   $1:$2 (expected closed)"; fail=1; else echo "PASS closed $1:$2"; fi; }
INFERENCE=${INFERENCE:-inference.presence.internal}

case "${1:-}" in
  worker)
    for p in 22 8006; do expect_closed "${LAN_PROXMOX:?}" "$p"; done
    expect_closed 10.77.10.1 8006
    for p in 22 80 443; do expect_closed "${LAN_ROUTER:?}" "$p"; done
    for p in 5432 3900; do expect_closed data.presence.internal "$p"; done
    expect_closed core.presence.internal 3000
    for p in 8080 8188 8443 22; do expect_closed "$INFERENCE" "$p"; done
    if timeout 5 bash -c 'exec 3<>/dev/tcp/1.1.1.1/443' 2>/dev/null; then echo "PASS open   internet 1.1.1.1:443"; else echo "FAIL no internet egress"; fail=1; fi
    ;;
  core)
    expect_open data.presence.internal 5432
    expect_open data.presence.internal 3900
    getent hosts "$INFERENCE" >/dev/null && echo "PASS resolves $INFERENCE" || { echo "FAIL resolve $INFERENCE"; fail=1; }
    if [ "${INFERENCE_OFF:-0}" = 1 ]; then
      echo "SKIP inference gateway (INFERENCE_OFF=1: host B powered off, cloud-only mode, E-062)"
      expect_closed "$INFERENCE" 8443
    else
      expect_open "$INFERENCE" 8443
      for p in 8080 8188; do expect_closed "$INFERENCE" "$p"; done
    fi
    for p in 22 8006; do expect_closed "${LAN_PROXMOX:?}" "$p"; done
    ;;
  internet)
    code=$(curl -s -o /dev/null -w '%{http_code}' "https://${TEST_HOST:?}/")
    [ "$code" = 200 ] && echo "PASS $TEST_HOST -> 200" || { echo "FAIL $TEST_HOST -> $code"; fail=1; }
    loc=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' "https://${CONSOLE_HOST:?}/")
    case "$loc" in 30[23]\ https://*.cloudflareaccess.com/*) echo "PASS $CONSOLE_HOST -> Access sign-in";; *) echo "FAIL $CONSOLE_HOST -> $loc"; fail=1;; esac
    # Tunnel ingress needs no open ports: every common port on the site's public address must be closed.
    for p in 22 80 443 3000 3900 5432 6379 7233 8006 8007 8080 8188 8443 2375 2376; do expect_closed "${WAN_IP:?}" "$p"; done
    ;;
  *) echo "usage: $0 worker|core|internet" >&2; exit 2;;
esac
exit $fail
