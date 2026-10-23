# Treeneesu — Public Testnet Deployment Package (F-04)

**Nothing in this package is deployed.** No seed node, VPS, or DNS
record for Treeneesu exists today. This package is the complete,
ready-to-execute preparation so that the *owner* can provision a real
public testnet with no further engineering. Every step that needs an
account, a domain, a server, or money is marked **[OWNER ACTION]**.

## Why this is needed (audit F-04)

Treeneesu main has *no* peer-discovery: DNS seeds and fixed seeds were
deleted by design, so a node started with default flags finds zero
peers forever. A public testnet needs three ingredients the project
does not currently have:

1. **Bootstrap nodes** — always-on nodes at stable addresses that new
   nodes can connect to first.
2. **A DNS seed** — a hostname whose DNS answers return bootstrap node
   IPs, so `vSeeds` has something real to point at.
3. **Operators** — at least three independently operated machines
   (Gate C), with monitoring.

## Architecture (minimum viable public testnet)

| Role | Count | Spec (sufficient) |
|---|---|---|
| Seed/bootstrap node | 3 | 1 vCPU, 1 GB RAM, 20 GB disk, static IPv4, ports 29333 open |
| DNS seed host | 1 | any DNS provider supporting dynamic A-record updates |

All three seed nodes run the identical configuration in
`seed-node/` (systemd unit + `treeneesu.conf`), differing only in
datadir host. Each lists the other two via `-addnode` so the seed set
is internally meshed even before the DNS seed exists.

## Owner provisioning checklist

1. **[OWNER ACTION]** Rent 3 small VPS instances in different
   providers/regions. Record their public IPv4 addresses.
2. **[OWNER ACTION]** Point DNS: create `seed.treeneesu.<domain>` —
   actually a dedicated subdomain, e.g. `tnsu-seed.example.com` — as
   A records naming all 3 seed IPs. (One hostname, three A records;
   that *is* the DNS seed.)
3. On each VPS: install the node from the release source, copy
   `seed-node/treeneesu.conf` (fill in the other seeds' IPs), install
   `seed-node/treeneesu-node.service`, enable and start it.
4. Verify from a *fourth*, unrelated machine: start a node with only
   `-connect=<any seed IP>:29333`, confirm sync; then start one with
   defaults after step 5.
5. **Only after steps 1–4 work:** submit the one-line code change that
   points `vSeeds` at the real hostname in
   `src/kernel/chainparams.cpp` (marked `OWNER-SEED-HOSTNAME` in the
   release checklist), rebuild, re-run the full unit suite, and cut a
   new release. Inventing the hostname before the DNS exists is
   explicitly forbidden by the audit rules.
6. Run the multi-host soak (`deploy/soak/multihost-soak.sh`) for the
   Gate C evidence window (≥2 weeks target, ≥72 h minimum for a first
   claim), including the partition and reorg drills in
   `deploy/soak/README.md`.

## What this package deliberately does not do

- It does not name a real hostname, IP, or provider (none exist).
- It does not create accounts, buy servers, or edit DNS (owner-only).
- It does not change the experimental/no-value status of the chain:
  a public *testnet* of a valueless chain is a testing exercise, and
  THREAT-MODEL.md §5 applies unchanged (difficulty is trivial; the
  testnet can and should be expected to get reorged by anyone bored).

## Monitoring (included)

`seed-node/check-node.sh` — run by cron or a systemd timer on each
seed; exits non-zero and prints a line if the node is down, block
height stalls >30 min, or peer count drops to zero. Wire its output
to whatever alerting the owner already uses; the script itself sends
nothing anywhere.
