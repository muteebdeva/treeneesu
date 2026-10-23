# Multi-host soak — what it proves and what it does not

Run `multihost-soak.sh` against ≥3 independently operated machines
(different providers/regions/networks) after the deployment package in
`deploy/README.md` is live.

**Proves (with its timestamped output as evidence):**
- Independent nodes agree on the Treeneesu genesis and converge to one
  tip over real network links.
- A partitioned node that keeps mining alone re-converges on heal
  (longest-work chain wins; losing-branch transactions return to the
  mempool or drop — at Treeneesu's difficulty this drill is *expected*
  to show the partition's blocks being orphaned, which is the correct
  consensus outcome and also a live demonstration of THREAT-MODEL.md
  §5: reorganizations here are cheap, by design).
- Daemon restarts preserve chain state exactly.

**Does not prove:**
- Resistance to a deliberate, resourced attacker (impossible at this
  difficulty; see THREAT-MODEL.md §5.3 — no confirmation count is
  safe, and this soak must never be cited as evidence of economic
  finality).
- Long-duration stability: a single scripted run is a drill. Gate C's
  soak criterion is ≥72 h of monitored uptime (target 2 weeks) with
  `check-node.sh` output retained, plus one clean drill run inside
  that window.

Local dry-run note: the same script logic was exercised in loopback
form by `testnet-run.sh` (3 nodes, one VM) — useful for debugging the
script, worthless as Gate C evidence. Only the multi-host run counts.
