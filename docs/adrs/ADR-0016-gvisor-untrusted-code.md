# ADR-0016 — gVisor for Untrusted Code/Build Workers
Status: Accepted

## Decision
Use gVisor or an equivalent strong sandbox for untrusted/generated code workers, with restricted network and no management/private-network reachability.
