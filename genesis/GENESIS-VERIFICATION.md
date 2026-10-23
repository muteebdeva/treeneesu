# Treeneesu MAIN genesis — pre-patch verification (2026-10-23)
Required by Muteeb before Patch 2a was applied. Method: replicate Bitcoin Core
v32.0 `CreateGenesisBlock` (src/kernel/chainparams.cpp:37) byte-for-byte in
Python (`genesis/grind_genesis.py`), prove the replica on Bitcoin itself, then
construct + grind Treeneesu's block.

## Control test (proves the construction code is correct)
Feeding Bitcoin's own inputs (Satoshi timestamp text + pubkey, nTime 1231006505,
nBits 0x1d00ffff, nNonce 2083236893, 50 BTC) reproduces, exactly:
- merkle root 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b ✅
- genesis hash 000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f ✅

## Treeneesu main genesis (verified twice: grind + independent recompute)
- pszTimestamp: `Treeneesu 23/Oct/2026 - a learning chain with no monetary value`
  (ASCII hyphen — D5's em-dash replaced so the scriptSig bytes are unambiguous)
- nTime: 1792713600 (2026-10-23 00:00:00 UTC) · nVersion: 1 · reward: 50 TNSU
- Output script: <65-byte uncompressed secp256k1 pubkey> OP_CHECKSIG, pubkey hex:
  048439b61821b6aa12b1323804f36205c9ddf372a6a3baa6d3732b882af3c1e2516425bc7e85257
  c10ce7fb243c9b9bc61fbfb3359582760c8d78d6d0f9e50a478 (freshly generated for
  Treeneesu; NOT Satoshi's key)
- nBits: 0x1e0fffff → target 00000fffff000000000000000000000000000000000000000000000000000000
- nNonce ground: **535382** (535,383 tries, ~1.3 s)
- **Merkle root: 9b242aa5c3f7c5478b6285a1f073f202994dc41dd58bcea70680102b6a2096cf**
- **Genesis hash: 000008c949ab6dfa087901003f3f05804bd550bb9a094fc57ecec54994c015b6**
- PoW check: hash ≤ target ✅ (000008c9… < 00000fff…)
- Final cross-check pending in Patch 2a itself: bitcoind's in-code asserts and
  `getblockhash 0` must reproduce this hash from the compiled code.

## Coinbase spendability (verified in source, not assumed)
Upstream's own comment above CreateGenesisBlock (kernel/chainparams.cpp):
"the output of its generation transaction cannot be spent since it did not
originally exist in the database." Mechanism: `ChainstateManager::LoadGenesisBlock`
(src/validation.cpp:4945) writes the genesis block to disk directly; its
coinbase outputs never enter the UTXO set, so no later transaction can spend
them. Treeneesu inherits this unchanged: **the 50 TNSU genesis reward is
unspendable by construction**, exactly like Bitcoin's genesis reward.

---

## Amendment 2026-10-23 — powLimit fix (owner decision: Option A)

The original powLimit (bits 0x1e0fffff, target ≈ 2^236) violated the
retarget overflow invariant powLimit < 2^256 / (4 × nPowTargetTimespan)
≈ 2^233.8 (found by pow_tests; see MISSION2-CHANGELOG.md). The owner chose
Option A: bits **0x1e01ffff**. The genesis block was therefore re-ground
with the identical coinbase (same message, timestamp, pubkey, reward —
merkle root unchanged: 9b242aa5…96cf):

- **nBits: 0x1e01ffff**, powLimit target hex:
  000001ffff000000000000000000000000000000000000000000000000000000
- **nNonce: 26434925** (26,434,926 tries)
- **Genesis hash: 00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee**
- PoW check: hash ≤ target ✅ (00000091… < 000001ff…)
- Genesis work (GetBlockProof): **0x800040** → nMinimumChainWork updated.
- Dependent updates in chainparams.cpp: powLimit, genesis call
  (nonce/bits), hashGenesisBlock assert, BIP34Hash. The pre-change control
  discipline was kept: the grinding program first re-verified Bitcoin's
  genesis construction (known nonce 2083236893 → hash 000000000019d668…26f).
- The superseded v1 genesis (hash 000008c9…015b6, nonce 535382) belongs to
  the defective parameter set and must not be used.
