# Treeneesu — honest portfolio summary

**What it is.** A from-source modification of Bitcoin Core v32.0 into an
independent proof-of-work cryptocurrency: new genesis block, network magic,
ports, address formats, and a 42M-cap monetary policy, developed and tested
entirely on a 2-core VM at zero budget.

**What I can claim (each with evidence in this workspace).**
- Built the upstream tree from source and ran its full test suite
  (827/827 tests at baseline).
- Designed chain parameters (supply math verified exactly:
  41,999,999.9538 TNSU total issuance) and ground a custom genesis block,
  validating the grinding tool against Bitcoin's known genesis first.
- Applied the parameter patch; when the test gate failed, root-caused a
  suite "hang" to an assert-abort + crash-handler deadlock using gdb stack
  traces — not guesswork.
- Audited all 152 unit suites, classified every failure (identity fixtures
  vs parameter fixtures vs magic-dependent vectors vs one genuine design
  defect), and repaired them without deleting or weakening a single test:
  payload-preserving re-encodings, dual-verified (Python + C++ oracle)
  descriptor checksum/hash recomputation, an independent Python BIP324
  implementation that reproduced Bitcoin's vectors byte-for-byte before
  generating Treeneesu's, 110 re-ground miner nonces, and two surgical
  fixture corrections (miner activation heights; a fake-clock interval).
  Result: 151/152 suites pass in one process.
- Found and characterized a genuine consensus-design defect (powLimit
  overflow at first retarget) and escalated it as a decision instead of
  silently changing consensus.
- Proved the chain works live: two nodes, no seeds, real proof-of-work,
  109 blocks, cross-node sync, a confirmed payment with satoshi-exact
  balances, restart recovery (scripted, re-runnable: `twonode-demo.sh`).
- Wrote the full documentation package (architecture, beginner's guide
  explaining every bug, command reference, runbook, troubleshooting,
  security/launch checklists) plus machine-readable test results.

**What I cannot claim.**
- Not a security audit; the "review" is a self-review with disclosed limits.
- Not production software: one blocking consensus parameter defect awaits
  an owner decision; developer chains (regtest/testnet) are not yet
  replaced; difficulty is intentionally trivial, so the chain has no
  meaningful attack resistance; the coins have no value.
- Nothing is published: all post-Patch-1 work is uncommitted in a local
  working tree, awaiting the owner's review.
