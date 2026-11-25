"""Offline checks of the R0-009 infrastructure files: the exposure rules hold before anything is applied."""

import re
import unittest
from pathlib import Path

INFRA = Path(__file__).resolve().parents[1]
FW = INFRA / "proxmox" / "firewall"
VMS = {"110": "edge", "120": "core", "130": "data", "140": "worker"}
HOST_BRIDGE_IPS = {"10.77.10.1", "10.77.20.1"}


def parse_fw(path):
    """Return ({option: value}, {ipset: [entries]}, [rule lines]) from a Proxmox .fw file."""
    options, ipsets, rules, section = {}, {}, [], None
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("["):
            section = line.strip("[]").split()
            if section[0] == "IPSET":
                ipsets[section[1]] = []
            continue
        if section[0] == "OPTIONS":
            key, value = (part.strip() for part in line.split(":", 1))
            options[key] = value
        elif section[0] == "IPSET":
            ipsets[section[1]].append(line)
        elif section[0] == "RULES":
            rules.append(line)
    return options, ipsets, rules


def arg(rule, flag):
    match = re.search(rf"{flag} (\S+)", rule)
    return match.group(1) if match else None


class FirewallTests(unittest.TestCase):
    def test_cluster_drops_inbound_and_limits_management_ports(self):
        options, ipsets, rules = parse_fw(FW / "cluster.fw")
        self.assertEqual(options["enable"], "1")
        self.assertEqual(options["policy_in"], "DROP")
        self.assertEqual(
            set(ipsets["private"]),
            {"10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10", "169.254.0.0/16"},
        )
        for rule in rules:
            self.assertTrue(rule.startswith("IN"), rule)
            self.assertEqual(arg(rule, "-source"), "+management", rule)

    def test_every_vm_drops_by_default(self):
        for vmid in VMS:
            options, _, _ = parse_fw(FW / f"{vmid}.fw")
            self.assertEqual(
                (options["enable"], options["policy_in"], options["policy_out"]),
                ("1", "DROP", "DROP"),
                vmid,
            )

    def test_every_inbound_accept_names_a_source(self):
        for vmid in VMS:
            for rule in parse_fw(FW / f"{vmid}.fw")[2]:
                if rule.startswith("IN") and "ACCEPT" in rule:
                    self.assertIsNotNone(arg(rule, "-source"), f"{vmid}: {rule}")

    def test_ssh_only_from_the_proxmox_host(self):
        for vmid in VMS:
            for rule in parse_fw(FW / f"{vmid}.fw")[2]:
                if rule.startswith("IN SSH"):
                    self.assertIn(arg(rule, "-source"), HOST_BRIDGE_IPS, vmid)

    def test_private_drop_precedes_general_egress(self):
        for vmid in VMS:
            outs = [r for r in parse_fw(FW / f"{vmid}.fw")[2] if r.startswith("OUT")]
            drop = outs.index("OUT DROP -dest +private")
            for rule in outs[drop + 1 :]:
                self.assertIsNone(arg(rule, "-dest"), f"{vmid}: {rule} after the private drop")

    def test_worker_reaches_nothing_private(self):
        outs = [r for r in parse_fw(FW / "140.fw")[2] if r.startswith("OUT")]
        self.assertEqual(outs[0], "OUT DROP -dest +private")

    def test_only_core_reaches_inference_and_data(self):
        for vmid in VMS:
            rules = parse_fw(FW / f"{vmid}.fw")[2]
            dests = {arg(r, "-dest") for r in rules if r.startswith("OUT ACCEPT")}
            if vmid != "120":
                self.assertNotIn("+inference", dests, vmid)
                self.assertNotIn("10.77.10.30", dests, vmid)
        data_in = {arg(r, "-source") for r in parse_fw(FW / "130.fw")[2] if r.startswith("IN ACCEPT")}
        self.assertEqual(data_in, {"10.77.10.20"})


class ProvisioningTests(unittest.TestCase):
    def test_every_vm_nic_has_the_firewall_on(self):
        script = (INFRA / "proxmox" / "vms.sh").read_text()
        nics = re.findall(r"--net\d+ \"([^\"]+)\"", script)
        self.assertTrue(nics)
        for nic in nics:
            self.assertIn("firewall=1", nic)
        for vmid in VMS:
            self.assertRegex(script, rf"\ncreate {vmid} ")

    def test_inference_host_drops_by_default(self):
        nft = (INFRA / "proxmox" / "inference-host.nft").read_text()
        self.assertIn("hook input priority filter; policy drop;", nft)
        self.assertNotRegex(nft, r"dport (8080|8188)")


class EdgeTests(unittest.TestCase):
    def test_edge_publishes_no_ports(self):
        compose = (INFRA / "compose" / "edge.compose.yaml").read_text()
        self.assertNotRegex(compose, r"(?m)^\s*ports:")
        self.assertNotIn("docker.sock", compose)
        for image in re.findall(r"image: (\S+)", compose):
            self.assertRegex(image, r"@sha256:[0-9a-f]{64}$")

    def test_caddy_binds_locally_without_admin_api(self):
        caddyfile = (INFRA / "compose" / "Caddyfile").read_text()
        self.assertIn("admin off", caddyfile)
        self.assertIn("default_bind 127.0.0.1", caddyfile)
        self.assertRegex(caddyfile, r"http://:8080 \{\s*respond 404")

    def test_tunnel_sends_everything_to_caddy(self):
        config = (INFRA / "cloudflare" / "cloudflared.yml").read_text()
        services = re.findall(r"service: (\S+)", config)
        self.assertEqual(services, ["http://127.0.0.1:8080"])


if __name__ == "__main__":
    unittest.main()
