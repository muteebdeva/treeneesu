# Treeneesu — Final Report (completion mission, 2026-10-23)

## Verdict

Treeneesu is a **genuinely functioning, independently verifiable blockchain**
on its own parameters: nodes mine real proof-of-work, sync, validate,
transact, reject invalid blocks, and recover from restarts — all proven by
executed tests and a scripted two-node demonstration, not by claims. It is a
**local development/learning network**. No public network exists, and the
coins have no monetary value.

## Exact identifiers

| Item | Value |
|---|---|
| Upstream base | Bitcoin Core v32.0 = `465dde277447e2f11e01bea09d2a094d7fb6ef45` |
| Local HEAD (source of the verified build) | `03727d8f962af23fd9dd02822430acfb5473c997` |
| Local commit chain | 5790ce2 → eca8485 → 35f49eb → 03727d8 (bundle: `history/treeneesu-commits.bundle`) |
| Genesis hash | `00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee` |
| GitHub repo | https://github.com/muteebdeva/treeneesu (private) |

## What works — with evidence

- **Independent identity**: own genesis/magic (a73e5c91)/ports
  (29333/29332)/address prefixes/bech32 HRP (tnsu)/datadir/UA; no seed
  nodes; cannot peer with Bitcoin (different magic + genesis).
  Verified in source, in the M4 audit, and live in the demo.
- **Consensus & PoW**: Bitcoin's retarget algorithm unchanged; parameters
  per PHASE2-DESIGN.md (150 s spacing, 8,064-block retarget, 50 TNSU
  subsidy, 420k halving, 42M cap). The one genuine consensus defect found
  (powLimit overflow) was fixed properly — in the parameters, not in the
  test that caught it.
- **Full unit suite: 152/152 suites, exit 0** (826/827 cases; the one
  warning case is upstream's env-gated script_assets self-skip).
  Log: `logs/final-fullrun/full2.log`.
- **Functional subset: ALL PASSED** (feature_help, rpc_net v1+v2,
  wallet_basic, p2p_v2_transport, feature_segwit, rpc_blockchain) against
  the final binaries. Log: `logs/functional-final.log`.
- **Two-node demo v2: ALL CHECKS PASSED** — sync of 109 real-PoW blocks,
  wallet payment of 25 TNSU confirmed with exact balance, overspend
  rejected, PoW-invalid block rejected (`high-hash`, tip unchanged),
  restart recovery. Log: `logs/twonode-demo-final.log`.
- **AddressSanitizer**: 12 key/repaired suites, all exit 0, zero reports.
  Log: `logs/asan-subset.log`.
- **Genesis**: three-way verified (source == independent Python ==
  compiled daemon). Record: `AUDIT-REPORT.md`.
- **Repository hygiene**: secret scan of the pushed tree — zero hits;
  `.gitignore` covers all build trees; the generated `test/config.ini`
  was excluded from the import explicitly.

## What failed along the way, and what fixed it

- **pow_tests (4 errors)** exposed the D4 powLimit defect → owner decision
  Option A → parameters fixed, genesis re-ground, test expectations
  recomputed via a control-verified independent model.
- **miner_tests (1 fatal error, first final run)** → fixture nonces were
  stale after the regrind → re-ground with the test's own construction;
  standalone pass, then the full rerun passed 152/152.
- **Infrastructure (not code)**: a VM replacement mid-session killed both
  builds and wiped apt packages; recovered via a workspace sysroot. The
  first GitHub tree upload (one giant POST) failed with HTTP 502;
  re-engineered to bottom-up tree creation. A demo attempt failed on a
  lost executable bit (log kept as logs/twonode-demo-attempt1-perms.log);
  relaunched clean. None of these were hidden.

## What remains unfinished — honestly

- **UBSan: not run** (disclosed in BLOCKERS B4; recommended before any
  public-network step).
- **Patch 2b/2c not done**: no Treeneesu-native test chain yet; the
  upstream testnet/signet classes remain in the binary with Bitcoin
  parameters (BLOCKERS B2).
- **Cosmetic rebrand deferred**: banner text and binary names (B6).
- **No tag / GitHub Release**: the RC notes stay a draft until the owner
  decides to publish a release (B5).
- **Public testnet/mainnet: not launched**, gated by
  MAINNET-READINESS-GATES.md (B7). Publishing source does not create a
  network; no independent participants exist yet.

## Addendum — completion phase (2026-10-23, later the same day)

Work done under the owner's "complete the project properly" brief, after
the report above was written:

- **UBSan: run and clean.** build-ubsan (SANITIZERS=undefined) exit 0 —
  interrupted once by a VM replacement at ~75%, completed incrementally.
  The 12-suite repaired/key subset: all exit 0, **zero UBSan runtime
  errors** (logs/ubsan-subset.log). BLOCKERS B4 is now fully closed
  (ASan + UBSan), with the subset scope disclosed.
- **Supply rules independently re-verified.** Subsidy, halving interval
  and MAX_MONEY read from source and reproduced by a Python model:
  boundary subsidies 50 → 25 → 12.5 TNSU, last nonzero era 32 (1 sat),
  total issuance 41,999,999.9538 TNSU (AUDIT-REPORT.md addendum 2).
- **Private testnet: PASSED.** testnet-run.sh (3 nodes, loopback IPs —
  network namespaces are unavailable on this VM) completed every check:
  genesis agreement, 105 blocks mined and synced with equal tips,
  10 TNSU transfer confirmed with satoshi-exact balance, wallet
  backup/restore with history intact, full restart recovery at
  height 106 (logs/testnet-run.log). Operator guide: TESTNET-GUIDE.md.
  The first attempt was killed mid-run by a VM replacement (its /tmp
  datadirs were wiped) and re-run from scratch; that history is kept,
  not hidden.
- **Retarget soak: PASSED (2026-10-24).** The result has landed:
  logs/retarget-assert-v2.log records all 8,070 blocks accepted by a
  fresh node, bits 1e01ffff @8063 → 1d7fffc0 @8064 and @8070 exactly as
  the independent model predicted, a second node synced to the
  identical tip, and the tip persisted a restart (RETARGET_EXIT:0).
  The road there is part of the record: the first ground chain was
  rejected at block 1 (bad-cb-height — the grinder encoded the BIP34
  height wrongly for heights 1–16; node validation was correct), the
  grinder was fixed and proven on a 20-block chain, and the full chain
  was re-ground under a self-healing supervisor across repeated VM
  replacements. MAINNET-READINESS-GATES.md Gate 1 is updated to MET.
  Full-suite sanitizer runs on the final tree also completed in this
  phase (UBSan exit 0, one triaged upstream report; ASan exit 0, zero
  errors). The overall readiness verdict does not change: B — public
  source-code release only.
- **Pushes.** This phase's work was pushed to the private repo in commit
  033e16ada192766977d8d46a4e6ab5b374fd3445 (on top of completion commit
  bee9406417e4…), remote-verified blob by blob.

## Bottom line for a reviewer

Clone `bitcoin-core/` from this repo, build with the README commands, run
`test_bitcoin` (expect all suites green), then run `twonode-demo.sh`
(expect ALL CHECKS PASSED), and compare `getblockhash 0` against the
genesis hash above. Every number in this report traces to a log file in
`logs/`.
