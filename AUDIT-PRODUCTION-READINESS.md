# Treeneesu — Independent Production-Readiness & Security Audit

**Date:** 2026-10-23 · **Auditor role:** independent protocol/security review
**Scope note:** this audit was performed with direct access to the
workspace, the local clone, the build trees, and the private GitHub
repository, and by re-executing selected tests during the audit. Where a
result could not be re-executed in audit time, it is classified by the
strength of its surviving evidence (log files tied to the audited tree),
never by documentation claims alone.

## Audited artifacts (exact)

| Artifact | Identity |
|---|---|
| Repository (private) | `github.com/muteebdeva/treeneesu`, branch `main` |
| Audited workspace commit | `9518eda31c65adebf71f96e2a1cffccbbeaf812e` |
| Embedded source clone HEAD | `03727d8f962af23fd9dd02822430acfb5473c997` (branch `treeneesu`) |
| Upstream base | Bitcoin Core v32.0, `465dde277447e2f11e01bea09d2a094d7fb6ef45` |
| Binaries audited | `bitcoin-core/build-final/bin/{bitcoind,bitcoin-cli,test_bitcoin}` built from the clone HEAD above |

## VERDICT

# B — READY FOR PUBLIC SOURCE-CODE RELEASE ONLY

Treeneesu's *source code* may be published. No Treeneesu *network* —
public testnet or mainnet — is approved by this audit, and the audited
commit must not be used with real funds under any circumstances.

**Would I personally approve this exact commit for production use
involving real funds? No.** The chain's proof-of-work difficulty is
~2²³ hashes per block (a single laptop CPU rewrites confirmed history
in seconds), its minimum-chain-work protection is exactly one block,
its difficulty retarget has never been observed live past the first
boundary, it has no peer-discovery mechanism, it has never run on more
than one physical machine, and no person independent of its author has
reviewed the changes. Each of those alone is disqualifying for real
funds; together they are not close.

---

## 1. Executive summary (plain English)

Treeneesu is Bitcoin Core v32.0 with a very small, well-isolated set of
parameter changes: a new genesis block, network magic and ports, address
prefixes, a 42M supply cap, 150-second blocks, and all seed nodes
removed. Every consensus *mechanism* — block/transaction validation,
proof-of-work checking, the retarget algorithm, chain selection,
timestamps, mempool, networking, wallet cryptography — is byte-for-byte
upstream code. That is the project's greatest strength: the risky part
of a fork is confined to 5 production files (58 insertions, 98
deletions), and this audit read every line of that diff.

The parameter change itself contained one genuine consensus defect
(the original proof-of-work limit would have broken the chain's
difficulty at the first retarget, block 8064). It was caught by the
upstream test suite before any network existed, fixed by an explicit
owner decision, and the fix was verified three independent ways. That
history cuts both ways: the process worked, but it proves the parameter
set was *not* safe as first designed — and the one live behaviour that
defect concerned, the retarget at block 8064, has still never been
executed end-to-end. The soak test that would prove it is ~8% complete
at audit time.

Testing evidence is unusually well preserved (full logs in the repo),
and this audit re-ran spot checks that reproduced the claimed results.
But all runtime evidence comes from one 2-core VM, from loopback
networking, operated by the author. There is no independent reviewer,
no CI, no fuzzing, no reproducible-build verification, and sanitizer
coverage is a 12-of-152-suite subset.

As *published source code* — an educational fork with honest "no
monetary value" labelling, a clean MIT licence, and no secrets in the
tree — Treeneesu is safe to release. As a *network* it is a
single-machine demonstration, and as a *store of value* it would be
defenceless.

## 2. What was independently verified vs. merely documented

**Re-executed during this audit (auditor-observed):**
- Full production diff read line-by-line (5 files; §3).
- Fresh node start from the audited binaries: `getblockhash 0` =
  `00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee` ✔;
  reported difficulty 0.0019531 (consistent with bits 0x1e01ffff).
- `pow_tests` re-run: exit 0. `validation_tests` re-run: exit 0
  (7/7 cases).
- Repository hygiene: licence file, secret pattern scan (no hits), no
  `wallet.dat`/`.env` in tree, no CI directory at repo root.

**Verified from surviving logs tied to the audited tree (not re-run):**
- Full unit suite: `logs/final-fullrun/full2.log` ends "Test module …
  has passed" (152/152 suites; 826/827 cases, 1 warning = upstream
  optional-data self-skip in `script_assets_tests`).
- Functional subset (7 scripts): `logs/functional-final.log` —
  ALL Passed, exit 0.
- Two-node demo: `logs/twonode-demo-final.log` — ALL CHECKS PASSED.
- ASan subset: `logs/asan-subset.log` — 12 suites exit 0, zero reports.
- UBSan subset: `logs/ubsan-subset.log` — 12 suites exit 0,
  `RUNTIME_ERRORS:…:0` for every suite, zero "runtime error" lines.
- Private testnet: `logs/testnet-run.log` — ALL CHECKS PASSED, exit 0
  (details §5; note its first attempt was destroyed by a VM replacement
  and the log records the successful re-run).

**Documented only / not verified:**
- Anything about behaviour on other machines, operating systems, or
  real networks: no evidence exists.
- The retarget soak: **incomplete** (§4 of the brief; finding F-02).

## 3. Consensus & correctness audit (the production diff)

All changes vs. upstream `465dde27…` — 26 files total: **5 production**,
19 unit-test files, 2 functional-framework files. No changes to
`src/pow.cpp`, `src/validation.cpp`, `src/chain.cpp`, `src/net*`,
`src/wallet/*` production code, build system, or dependencies.

`src/kernel/chainparams.cpp` (CMainParams only; 2 hunks, both in the
main class — the testnet/testnet4/signet/regtest classes are untouched
upstream code, see F-05):
- `powLimit = 0x000001ffff00…00` (bits 0x1e01ffff). Satisfies the
  retarget overflow invariant `powLimit < 2^256/(4·timespan)` ≈ 2^233.79
  that the original value (0x1e0fffff ≈ 2²³⁶) violated. Verified
  consistent with `pow_tests` sanity (re-run, exit 0) and with the
  daemon-reported difficulty.
- Genesis: `CreateGenesisBlock("Treeneesu 23/Oct/2026 - a learning
  chain with no monetary value", …, 1792713600, nonce 26434925,
  0x1e01ffff, 1, 50·COIN)`; asserted hash and Merkle root match the
  values a fresh daemon computes (re-verified live, §2). The genesis
  output pays to a pubkey script in the usual upstream style; the
  genesis coinbase is unspendable by construction (never enters the
  UTXO set) on any Bitcoin-derived chain.
- `nSubsidyHalvingInterval = 420000`, spacing 150 s, retarget period
  8064 blocks / 14 days. Supply: `src/consensus/amount.h`
  `MAX_MONEY = 42,000,000·COIN`; the subsidy schedule sums to
  41,999,999.9538 TNSU (independently modelled; matches the
  `validation_tests` constant, which this audit re-ran green).
  `GetBlockSubsidy` itself is upstream code.
- Activation heights: BIP34/65/66/CSV = 1, SegWit = 0,
  `MinBIP9WarningHeight = 0`, BIP9 TESTDUMMY period/threshold correctly
  rescaled to 8064/7258. Bitcoin's `script_flag_exceptions` and
  assumeutxo snapshots were correctly deleted (they reference Bitcoin
  blocks that can never occur here). `defaultAssumeValid = 0` —
  no trusted block is smuggled in. All correct practice for a new chain.
- `nMinimumChainWork = 0x800040` — **exactly the genesis block's work**
  (see F-03).
- Network identity: magic `a7 3e 5c 91`, P2P 29333, RPC 29332
  (`src/chainparamsbase.cpp`), all DNS seeds and fixed seeds deleted in
  code (confirmed in the diff, not just in docs).
- Address formats: base58 PUBKEY 65 ("T…"), SCRIPT 22, SECRET 193;
  bech32 HRP `tnsu`; extended-key prefixes `02FE6D4F`/`02FE6D47` are
  **arbitrary and unregistered** (admitted in code comments; F-06).

`src/common/args.cpp`, `src/clientversion.cpp`: datadir `.treeneesu`,
config `treeneesu.conf`, user-agent name `Treeneesu`. Cosmetic and
safe. Binary names and the "Bitcoin Core version" startup banner are
unchanged (disclosed in BLOCKERS B6; a user-confusion nit, not a
security issue).

**Consensus-split assessment:** because validation/PoW/retarget code
is unmodified upstream and every node runs identical parameters, two
correctly built Treeneesu nodes cannot diverge on any input this audit
could construct from the diff. The realistic split risk is
*configuration*, not code: the untouched Bitcoin-parameter chain
classes (F-05) and the absence of any checkpoint/seed infrastructure
mean "the network" is whatever a given operator's binary and
`-connect` flags say it is.

## 4. The difficulty-retarget test — INCOMPLETE

Design (sound): an independent C++ grinder (`retarget-test/
grind_chain.cpp`, linked against the audited build's own SHA-256
objects, SHA-NI enabled) constructs coinbase-only blocks 1..8070 with
5-second timestamp spacing; blocks 1..8063 at bits 0x1e01ffff, blocks
8064+ at the model-predicted bits 0x1d7fffc0. The prediction comes from
an independent Python model of `GetNextWorkRequired` that was
control-verified against all four upstream `pow_tests` expectations
*and* against the originally observed failing value. The assertion
phase (`retarget-test/submit_and_assert.sh`) submits the chain to two
fresh audited daemons via `submitblock` — every block is fully
validated by real consensus code, and the script asserts the bits at
heights 8063/8064/8070 on both nodes plus restart persistence. If run
to completion, this *is* a genuine consensus test of the retarget, not
block generation theatre.

Status at audit time: **640 of 8,070 blocks ground; assertion phase not
started.** The grind has been interrupted by three VM replacements and
resumed from its per-block checkpoint file each time (resume logic
verified in source and observed in logs). **No conclusion about
retarget behaviour may be drawn yet.** This audit explicitly does not
infer success from progress.

Known limits of the test even when complete: timestamps are synthetic
(uniform 5 s spacing drives the timespan clamp to exactly ¼×; other
timespan paths — slow-period ÷ up-to-4× easing, off-by-one window
edges, MTP interactions with realistic timestamps — are covered only by
upstream `pow_tests`, not live); blocks are coinbase-only (no
transaction load); both assertion nodes run on the same machine.

## 5. Network & distributed-systems readiness

Evidence base: a 2-node demo and a 3-node exercise, all on **loopback
IPs on one VM**, author-operated. Within that scope the evidence is
real: genesis agreement, block sync with equal tips, a confirmed
10 TNSU transfer with satoshi-exact balances, wallet backup/restore
with history intact, restart recovery at height 106
(`logs/testnet-run.log`).

Against public-internet operation, the gaps are structural:

- **No peer discovery exists.** DNS seeds and fixed seeds were deleted
  (deliberately). A public node started with default flags finds zero
  peers, forever. There is no seed infrastructure to audit — it does
  not exist (F-04).
- **Never multi-machine.** No Treeneesu node has ever run on a second
  physical machine, behind NAT, over a WAN, or under packet loss.
  Partition/reorg behaviour under adversarial conditions is untested
  on these parameters; with 150 s blocks at 2²³ difficulty, deep
  reorgs are cheap to manufacture (F-01/F-03).
- **Sybil/eclipse resistance** rests entirely on upstream addrman
  behaviour with manually introduced peers — untested here, and
  `nMinimumChainWork` = one block provides no anchor.
- **Operations:** no monitoring, no alerting, no incident procedure, no
  second operator, no upgrade/rollback rehearsal. The runbook documents
  single-node care only.
- The passing testnet run's peer counts were A=2 B=1 C=1 (disclosed in
  the log): sync completed through one hub node. Fine for a demo;
  it is not evidence of mesh resilience.

## 6. Security audit

**Inherited posture.** The overwhelming majority of the attack surface
(parsing, P2P, RPC, wallet crypto) is upstream Bitcoin Core v32.0,
unmodified. That code carries upstream's own review and fuzzing
history — but Treeneesu's *build* of it has had no independent review,
and upstream's assurance does not automatically transfer to a new
parameter regime (e.g., 150 s blocks and near-zero difficulty change
DoS economics: headers are almost free to produce in bulk, even though
each must still be individually valid).

**What this audit checked directly:**
- The full production diff (above): no unsafe parsing, no new network
  code, no RPC surface changes, no dangerous defaults introduced.
  RPC remains localhost-by-default upstream behaviour; the operator
  guide correctly warns against exposing it.
- Secret/credential scan of the tree: no private keys, tokens, or
  `.env`/`wallet.dat` files (the one credential incident in the
  project's history — a GitHub PAT pasted in a chat — was never used,
  stored, or committed; it appears nowhere in the tree; revocation is
  still an outstanding owner chore, outside this codebase).
- Wallet: upstream descriptor wallet, unmodified; backup/restore
  demonstrated once, by the developer (§5). Key generation is upstream
  (OS CSPRNG via Bitcoin Core's RNG); no Treeneesu code touches it.
- Transaction malleability/replay: SegWit active from height 0;
  chain-unique magic, ports, address formats, and genesis make
  cross-chain replay with Bitcoin a practical non-issue; no
  Treeneesu-specific replay vector arises from the diff.
- Sanitizers: ASan and UBSan builds (exit 0) ran a **12-suite subset**
  (pow, miner, bip32, bip324, descriptor, key, key_io, transaction,
  validation, denialofservice, bloom, coins) — all exit 0, zero
  reports. Honest limits: that is 12 of 152 suites; ASan ran with
  `detect_leaks=0` (disclosed in TEST-SUMMARY.json); no sanitizer node
  soak, no fuzz target runs, no coverage data. These runs are evidence
  about those suites only — they do not establish memory safety of the
  whole node, and this audit does not claim otherwise.
- Dependencies: identical to upstream v32.0 (no additions); dependency
  risk is whatever upstream v32.0 carries, plus the local build used a
  workspace-extracted sysroot of Ubuntu packages after a VM incident —
  build provenance is "one author's laptop-class VM", with no
  reproducible-build (Guix) attestation and no signed artifacts.

**Not performed (insufficient evidence, stated plainly):** no fuzzing,
no full-suite sanitizer run, no penetration test of a live node, no
review of upstream code beyond the diff, no dependency CVE sweep, no
multi-machine or adversarial-network testing, no third-party review of
any kind. Any of these could, in principle, surface findings this
audit cannot see.

## 7. Licensing & release readiness

- `bitcoin-core/COPYING` (MIT, © Bitcoin Core developers) is present
  and untouched; modified files retain upstream headers (the diff does
  not touch any file header). MIT obligations for source distribution
  are satisfied. No licence contamination was introduced (no new
  dependencies or copied code in the diff).
- The README states prominently that the coins are experimental and
  have **no monetary value**, that this is a learning network, and how
  to build/run it. TESTNET-GUIDE.md documents wallet backup/recovery
  (developer-tested only). Known limitations are unusually well
  documented (BLOCKERS.md, MAINNET-READINESS-GATES.md).
- Missing for a *release* (as opposed to source publication): versioned
  release artifacts, checksums/signatures, a support/upgrade policy,
  and any CI. RELEASE-NOTES-v0.1.0-rc1.md is an unpublished draft.

## 8. Findings (severity-ranked)

| # | Severity | Finding | Evidence |
|---|---|---|---|
| F-01 | **Critical** (for any value-bearing use) | Difficulty is ~2²³ hashes/block (bits 0x1e01ffff; daemon-reported difficulty 0.00195). Any single commodity CPU can out-mine the entire honest network and rewrite confirmed history at will. The chain has no meaningful attack resistance — by design, but absolutely. | `src/kernel/chainparams.cpp` powLimit; live `getblockchaininfo` during audit |
| F-02 | **High** | The difficulty retarget at block 8064 — the exact behaviour the project's one real consensus defect concerned — has never been executed live. The soak test is 640/8070 blocks complete; the assertion phase has not run. Retarget correctness currently rests on unit tests + a model, not observation. | `retarget-test/blocks.txt`, `retarget-test/grind.log` (audit-time state) |
| F-03 | **High** | `nMinimumChainWork = 0x800040` = the work of the genesis block alone. A fresh node will accept any fork from genesis with marginally more work; combined with F-01 there is no objective anchor for "the real chain". | `src/kernel/chainparams.cpp` |
| F-04 | **High** (for public-testnet use) | No peer discovery: DNS seeds and fixed seeds are deleted and no replacement bootstrap exists. A public network cannot form without out-of-band manual peering by every participant. | Diff (§3); TESTNET-GUIDE.md §7 |
| F-05 | **Medium** | Non-main chain classes (testnet, testnet4, signet, regtest) remain **Bitcoin-parameter** classes inside a Treeneesu-branded binary/datadir (diff hunks touch CMainParams only). `-chain=test` etc. silently run Bitcoin chains; a confusion and footgun risk for operators and a correctness trap for future work. | `git diff` hunk map of `src/kernel/chainparams.cpp`; BLOCKERS B2 |
| F-06 | **Medium** | Extended-key prefixes (0x02FE6D4F/0x02FE6D47) are arbitrary and unregistered. Collision with another chain's/wallet's prefixes can cause cross-software confusion of extended keys. Bech32 HRP `tnsu` is likewise unregistered (lower risk: HRP collisions mainly affect address parsing UX). | `src/kernel/chainparams.cpp`; PHASE2-DESIGN.md D7 |
| F-07 | **Medium** | All runtime evidence is single-machine, single-operator, loopback-only. No multi-host, NAT, WAN, partition, or adversarial testing exists. Demo success is being asked to carry weight it cannot carry if cited as network evidence. | `logs/twonode-demo-final.log`, `logs/testnet-run.log` (datadirs /tmp, bind 127.0.0.x) |
| F-08 | **Medium** | Test-evidence breadth is narrower than the headline numbers suggest: functional coverage is 7 of upstream's ~200+ functional tests; sanitizer coverage is 12 of 152 suites per sanitizer; the full unit suite's 152/152 includes 19 test files *repaired by the author* (payload-preserving, documented in MISSION2-CHANGELOG.md — but the repairs were reviewed by no one). | TEST-SUMMARY.json; MISSION2-CHANGELOG.md; `logs/functional-final.log` |
| F-09 | **Low** | No CI runs on this repository (upstream `.github` sits in a subdirectory where GitHub Actions ignores it), no reproducible-build verification, no signed/checksummed release artifacts. Regressions would be caught only by manual local runs. | Repo root listing (no `.github`); absence of Guix attestations |
| F-10 | **Low** | Build provenance fragility: the development VM was replaced three times in one day; dependency state now lives in a workspace sysroot of extracted .debs. Builds are reproducible in the loose sense (documented commands, clean-build exit 0) but the environment is not a controlled release environment. | TEST-SUMMARY.json environment note; BLOCKERS B8 |
| F-11 | **Informational** | Startup banner still prints "Bitcoin Core version v32.0.0" and binaries are named bitcoind/bitcoin-cli. Cosmetic; disclosed (BLOCKERS B6). Could confuse users about what software they run. | Observed in node logs |
| F-12 | **Informational** | The original powLimit defect (pre-fix) would have stalled difficulty adjustment at the first retarget. It was caught pre-launch by upstream's own sanity test and fixed transparently — evidence *for* the project's process, recorded here because any honest audit of this codebase must note its parameters were not right the first time. | AUDIT-REPORT.md; PHASE2-DESIGN.md amendment; commit `35f49eb` |

No other defects were found in the production diff. In particular: no
issuance path exceeds the modelled supply; no seed, checkpoint, or
trusted-block data is smuggled in; no validation rule is weakened
relative to upstream.

## 9. Test inventory

| Test / evidence | Status | Basis |
|---|---|---|
| Unit suite, full (152 suites) on final tree | **Passed** | Log inspected; spot suites re-run green in audit |
| pow_tests / validation_tests (audit re-run) | **Passed** | Auditor-executed, exit 0 |
| Fresh-node genesis & difficulty (audit) | **Passed** | Auditor-executed |
| Functional subset (7 scripts) | **Passed** | Log inspected (ALL Passed, exit 0) |
| Two-node demo (sync, payment, invalid-block rejection, restart) | **Passed** | Log inspected |
| ASan subset (12 suites) | **Passed, zero reports** | Log inspected; subset scope + `detect_leaks=0` disclosed |
| UBSan subset (12 suites) | **Passed, zero reports** | Log inspected |
| Private testnet (3-node, transfer, backup/restore, restart) | **Passed** | Log inspected (re-run after VM loss of first attempt) |
| Supply schedule model vs. source | **Passed** | AUDIT-REPORT.md addendum 2; constants consistent with re-run validation_tests |
| **Retarget soak (blocks 1..8070 + assertions)** | **INCOMPLETE** | 640/8070 ground at audit time; assertion phase not run |
| Full functional suite (~200+ scripts) | **Not run** | Only the 7-script subset was executed |
| Full-suite ASan/UBSan | **Not run** | Subsets only |
| Fuzz targets | **Not run** | No evidence exists |
| Multi-machine / WAN / partition tests | **Not run** | Never attempted |
| Reproducible (Guix) build verification | **Not run** | No attestations exist |
| Independent third-party review | **Does not exist** | Gate 2 of MAINNET-READINESS-GATES.md unstarted |

## 10. Release blockers & acceptance criteria

**For an experimental public testnet (status C)** — all required:
1. Retarget soak completes and `submit_and_assert.sh` passes on the
   audited tree (bits at 8063/8064/8070 as predicted, both nodes,
   restart persistence). *Closes F-02.*
2. A bootstrap mechanism exists and is documented (fixed seed nodes
   operated for the purpose, or an equivalent reviewed design).
   *Closes F-04.*
3. ≥3 nodes on ≥3 independently operated machines on the public
   internet sustain sync for ≥2 weeks including at least one
   partition-and-heal and one deep-reorg drill, with logs published.
   *Addresses F-07, partially F-03.*
4. F-05 resolved or explicitly accepted in writing by the owner
   (Bitcoin-parameter chain classes removed, replaced, or fenced off).
5. A named operator, monitoring of height/peers, and a published
   halt/restart contact exist.

**For production candidacy (status D)** — everything above, plus:
6. Difficulty and `nMinimumChainWork` raised to values with a written
   security argument, OR the project's scope formally remains
   "no value, ever" — in which case D is unreachable by definition.
   *Closes F-01/F-03 for any value-bearing claim.*
7. Independent review of the full production diff by a reviewer who
   did not write it, with written sign-off; full functional suite run;
   full-suite sanitizer runs; a fuzzing campaign with published
   corpus/results.
8. Reproducible builds verified from a clean machine by a second
   person; signed release artifacts; upgrade/rollback rehearsal.

## 11. Remediation plan (priority order)

1. Finish the retarget soak; publish its full logs either way.
2. Decide F-05 (strip or replace the Bitcoin chain classes).
3. Run the full functional suite against Treeneesu parameters; log it.
4. Full-suite ASan+UBSan runs; then a bounded fuzz campaign
   (fuzz targets exist upstream; run them against this build).
5. Add root-level CI that builds and runs the unit suite on every push.
6. Multi-machine testnet exercise (§10.3) before any public exposure.
7. Register or deliberately re-choose extended-key prefixes/bech32 HRP;
   document the decision.
8. Guix reproducible build + second-person verification before any
   artefact is called a "release".

## 12. What is safe, precisely

- **Safe to publish on GitHub (public source):** the audited tree —
  licence-clean, secret-free, honestly labelled as experimental and
  valueless, with its limitations documented in-repo. Publication
  should keep the README's no-value statements prominent.
- **Safe as a public testnet:** **not yet** — §10 items 1–5 are unmet
  (bootstrap does not exist; retarget unverified live; single-machine
  evidence only).
- **Safe for real financial transactions:** **no** — F-01 and F-03 make
  theft-by-rewrite a matter of seconds of commodity compute, and no
  remediation short of a new parameter set (a new chain) changes that.

## 13. Conditions under which this verdict changes

- **B → C:** §10 items 1–5 all evidenced (soak passed, bootstrap live,
  multi-machine soak published, F-05 dispositioned, operator named).
- **C → D:** additionally §10 items 6–8 (a difficulty/security posture
  with a written argument, independent review, full test/sanitizer/fuzz
  evidence, reproducible signed releases).
- **B → A (downgrade):** discovery of a secret, licence defect, or
  undisclosed consensus change in the tree; or publication framing
  that presents Treeneesu as production-ready or value-bearing.
- Any change to the 5 production files invalidates this audit's diff
  review and requires re-audit of the delta.

*End of audit. This document evaluates the artifacts listed at the top
and no others; it is not a guarantee that the code is free of defects —
it is a statement of what the available evidence does and does not
establish.*

---

## ADDENDUM — Readiness-phase results (2026-10-24)

Added after the production-readiness engineering phase executed the
plan this audit informed. The original verdict is **unchanged**.

**Gate A (source release): met** (unchanged).

**Gate B (consensus soak): MET.** The F-02 retarget soak completed
(logs/retarget-assert-v2.log, exit 0): 8,070 offline-ground blocks were
submitted to a fresh node and fully accepted; bits at 8063/8064/8070
were 1e01ffff / 1d7fffc0 / 1d7fffc0 — exactly the independent model's
prediction (timespan clamped to ¼); a second node synced the identical
tip; the tip persisted a restart. The process caught a real defect on
the way: the first chain was rejected at block 1 (bad-cb-height)
because the *test grinder* encoded BIP34 heights 1–16 as data pushes
instead of OP_1..OP_16. Node validation was correct; the grinder was
fixed, proven on a 20-block chain, and the chain re-ground. The invalid
v1 chain is preserved (retarget-test/blocks-v1-bip34bug.txt) and the
episode is mapped in DEFECT-REGRESSION-MAP.md terms: live validation
is the guard.

**Sanitizer scope (F-08): closed.** Full-suite runs on the final
(F-05) tree: UBSan exit 0 (one report — src/streams.cpp:99, untouched
upstream code, empty-span fwrite, triaged benign in TEST-SUMMARY.json);
ASan exit 0, zero errors. Fuzzing remains unexecuted locally (no
clang/libFuzzer in the environment) and is noted as a CI-coverage item,
not a result.

**Other findings:** F-01 dispositioned as a permanent design property
(F01-POW-ANALYSIS.md; successor-chain preconditions defined — raising
difficulty in place was analysed and rejected). F-03 closed (tool
written, live-tested, one tool bug found and fixed). F-04 package
prepared; infrastructure remains owner-gated. F-05 closed (network
isolation, source commit 2ecd619). F-06 dispositioned (keep prefixes;
owner registers).

**Gate C (public testnet): NOT MET — blocked on owner infrastructure**
(seed host + DNS; deploy/ package is ready, nothing provisioned).
**Gate D (independent review): NOT MET** — all review remains
single-author. **Gates E/F: not reachable and not sought** for this
chain.

**Final decision: the audited verdict stands — B, READY FOR PUBLIC
SOURCE-CODE RELEASE ONLY.** This addendum strengthens the engineering
evidence behind that verdict; it does not raise it. The personal
answer also stands: this commit must not secure real funds.
