#!/usr/bin/env bash
# Creates the four R0 VMs and the nightly backup job (ADR-0009, ADR-0033 section 11).
# Run as root on the Proxmox host, after the bridges, firewall files and PBS storage exist
# (docs/runbooks/infrastructure-baseline.md). Sizes are proposals; see docs/infrastructure/topology.md.
set -euo pipefail

STORAGE=${STORAGE:-local-zfs}           # VM disk storage
PBS_STORAGE=${PBS_STORAGE:-pbs}         # storage ID given to `pvesm add pbs`
SSH_KEYS=${SSH_KEYS:?path to the operator public key file}
IMAGE=${IMAGE:-/var/lib/vz/template/debian-13-genericcloud-amd64.qcow2}   # checksum-verified Debian 13 cloud image
GW_SERVICES=10.77.10.1
GW_WORKER=10.77.20.1

[ -f "$IMAGE" ] || { echo "missing $IMAGE (see runbook step 3)" >&2; exit 1; }

create() { # id name cores memory_mb disk_gb bridge ip gateway
  qm create "$1" --name "$2" --ostype l26 --machine q35 --bios ovmf --cpu host \
    --cores "$3" --memory "$4" --scsihw virtio-scsi-single \
    --efidisk0 "$STORAGE:1,efitype=4m" \
    --scsi0 "$STORAGE:0,import-from=$IMAGE,discard=on,iothread=1" \
    --ide2 "$STORAGE:cloudinit" --boot order=scsi0 \
    --net0 "virtio,bridge=$6,firewall=1" \
    --ipconfig0 "ip=$7/24,gw=$8" --nameserver "1.1.1.1 9.9.9.9" --searchdomain presence.internal \
    --ciuser presence --sshkeys "$SSH_KEYS" \
    --agent enabled=1,fstrim_cloned_disks=1 --onboot 1 --serial0 socket --vga serial0
  qm disk resize "$1" scsi0 "${5}G"
}

create 110 edge   2  2048  20 vmbr1 10.77.10.10 "$GW_SERVICES"
create 120 core   4  8192  60 vmbr1 10.77.10.20 "$GW_SERVICES"
create 130 data   4  8192 200 vmbr1 10.77.10.30 "$GW_SERVICES"
create 140 worker 8 16384 200 vmbr2 10.77.20.10 "$GW_WORKER"

# Nightly snapshot backup of all four VMs to Proxmox Backup Server, after the 01:30 database dump.
pvesh create /cluster/backup --id presence-nightly --vmid 110,120,130,140 \
  --storage "$PBS_STORAGE" --schedule '02:30' --mode snapshot --enabled 1 \
  --prune-backups 'keep-daily=7,keep-weekly=4,keep-monthly=6' \
  --notes-template '{{guestname}}'

echo "Created VMs 110-140 and job presence-nightly. Start them with: for id in 110 120 130 140; do qm start \$id; done"
