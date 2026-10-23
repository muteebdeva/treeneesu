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
  Result: **152/152 suites pass** (826/827 cases; the one warning case is
  an upstream optional-data self-skip), re-verified on a clean rebuild
  from committed source.
- Found and characterized a genuine consensus-design defect (powLimit
  overflow at first retarget) and escalated it as a decision instead of
  silently changing consensus. The owner chose the fix (Option A: bits
  0x1e01ffff); the genesis was re-ground and verified three ways (source
  == independent Python == compiled daemon), and the pow_tests/miner_tests
  expectations were recomputed with an independent Python difficulty
  model that first reproduced all upstream values.
- Ran both sanitizers on the repaired/key 12-suite subset: ASan clean,
  UBSan clean (zero reports, all exit 0).
- Proved the chain works live: two nodes, no seeds, real proof-of-work,
  109 blocks, cross-node sync, a confirmed payment with satoshi-exact
  balances, restart recovery (scripted, re-runnable: `twonode-demo.sh`).
- Wrote the full documentation package (architecture, beginner's guide
  explaining every bug, command reference, runbook, troubleshooting,
  security/launch checklists) plus machine-readable test results.

**What I cannot claim.**
- Not a security audit; the "review" is a self-review with disclosed limits.
- Not production software: developer chains (regtest/testnet classes) are
  not yet replaced and still carry upstream parameters; difficulty is
  intentionally trivial, so the chain has no meaningful attack
  resistance; the coins have no value. Sanitizer coverage is a 12-suite
  subset, not the full suite; the live retarget soak past block 8064 was
  still running when this summary was updated (2026-10-23).
- Published only to a **private** GitHub repository
  (muteebdeva/treeneesu) with the owner's authorization: local commits
  5790ce2, eca8485, 35f49eb, 03727d8; remote main import 32451353… and
  completion commit bee94064…, plus later completion-phase updates.
  No tag, no GitHub Release, no public network — those remain separate
  owner decisions.
