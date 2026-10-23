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

## Bottom line for a reviewer

Clone `bitcoin-core/` from this repo, build with the README commands, run
`test_bitcoin` (expect all suites green), then run `twonode-demo.sh`
(expect ALL CHECKS PASSED), and compare `getblockhash 0` against the
genesis hash above. Every number in this report traces to a log file in
`logs/`.
