# Phase 3 — Patch 2 PLAN (for approval before applying; consensus-critical)

Patch 2 is split into 2a / 2b / 2c so each diff stays reviewable. Values are
exactly the approved Phase 2 design (D1–D8). Risk first, per the working rules.

## Patch 2a — Treeneesu MAIN parameters + MAX_MONEY (the big one)
Files: `src/kernel/chainparams.cpp` (CMainParams only), `src/consensus/amount.h`,
`src/chainparamsbase.cpp` (RPC base port).
Changes:
- Genesis: new pszTimestamp "Treeneesu 23/Oct/2026 — a learning chain with no
  monetary value"; nTime = build-day Unix time (fixed once, recorded);
  nBits 0x1e0fffff; nonce GROUND beforehand (see method below); genesis payout
  50 TNSU to a freshly generated Treeneesu pubkey (private key discarded —
  genesis coinbase is unspendable by construction, same as Bitcoin's).
- Params: halving 210000 → 420000; spacing 600 → 150; timespan stays 14 days
  (retarget every 8064 blocks); powLimit → 00000fffff…; fPowAllowMinDifficulty
  stays false; fPowNoRetargeting stays false.
- Activations: BIP34/65/66/CSV heights → 1, SegwitHeight → 0, BIP34Hash → new
  genesis hash; script_flag_exceptions DELETED; nMinimumChainWork → genesis
  work; defaultAssumeValid → 0; m_assumeutxo_data DELETED; chainTxData →
  genesis-only (time = genesis time, tx_count = 1).
- Network: magic f9beb4d9 → a73e5c91; port 8333 → 29333; RPC 8332 → 29332;
  vSeeds EMPTIED; vFixedSeeds EMPTIED.
- Addresses: base58 0/5/128 → 65/22/193; xpub/xprv → 02FE6D4F/02FE6D47;
  bech32_hrp bc → tnsu; silent_payments_hrp sp → tsp.
- amount.h: MAX_MONEY 21,000,000 → 42,000,000 * COIN (MoneyRange bound).
RISKS: (1) A wrong genesis assert = node won't start — caught instantly by
tests, fully reversible (local branch). (2) MAX_MONEY is a validity rule: any
block creating > cap must be rejected — covered by existing validation tests
run against new params + a new amount test. (3) Upstream mainnet-specific unit
tests WILL break (they assert Bitcoin genesis/prefixes — e.g. chainparams,
key_io fixtures). Those tests are updated to Treeneesu values in the same
patch; every change to a test is listed in the commit. Nothing is deleted to
make a failure disappear — fixtures get Treeneesu data.
Genesis grinding method (done BEFORE editing code, result recorded):
reconstruct the exact 80-byte genesis header in Python (coinbase built byte-
for-byte as CreateGenesisBlock does), double-SHA256, iterate nonce until
hash < target for bits 0x1e0fffff (~2^20 expected tries, seconds). Then the
found nonce + hash + merkle root go into the C++ asserts. Independent check:
after building, bitcoind itself re-derives the same hash at startup (assert)
and `getblockhash 0` must match the Python result.

## Patch 2b — Treeneesu REGTEST parameters
File: `src/kernel/chainparams.cpp` (CRegTestParams only).
New regtest genesis (own timestamp text/time, bits 0x207fffff, nonce ground the
same way), magic → b1c2d3e4, port 18444 → 29444, RPC → 29443, HRP bcrt →
tnsurt, base58 prefixes → same Treeneesu family as 2a (111/196/239 are
testnet's — replaced by regtest-specific values mirroring upstream structure:
use 65-family? NO — regtest must stay distinguishable from main: pubkey 80,
script 30, secret 208, HRP tnsurt; documented in the patch). Halving interval
keeps the upstream regtest value **150** (verified at v32.0) — regtest
deliberately deviates from main so subsidy behaviour is testable in a few
hundred blocks; that is upstream's own convention.
After 2b: re-run the Phase 1 regtest demo end-to-end on Treeneesu regtest.

## Patch 2c — Delete Bitcoin's other networks (D1 completion)
Delete CTestNetParams, CTestNet4Params, CSignetParams classes + their
chain-selection plumbing (`ChainType` cases in chainparamsbase/args where
safe), their seed data headers, and testnet-only test fixtures.
After 2c the binary contains NO Bitcoin network. This is the largest diff;
it lands last so 2a/2b are proven first. Functional tests that require
testnet/signet are removed with the networks (listed in commit).

## Order & gates
2a → build → full unit tests → commit. 2b → build → unit tests + regtest
demo → commit. 2c → build → unit tests → commit. Any gate failing stops the
sequence and gets reported, not patched over silently.
