# TREENEESU — Phase 2: Technical Design (PROVISIONAL — awaiting approval)

Status: **DRAFT v1, 2026-10-23. Nothing in this document is final until Muteeb
approves it. No code has been changed.** Every parameter marked ◆ is a decision
for approval (§10). Baseline: Bitcoin Core **v32.0** (tag, commit 465dde27),
already built and test-verified in Phase 1. All file:line references are to v32.0.

Safety frame (unchanged from the commission): development/testing only, private
local network, no real monetary value, no public mainnet, no token sale, ₹0.

---

## 1. Design approach — Decision D1 ◆

**Recommended: "replace-main" (the Litecoin-style fork).**
In this codebase, Treeneesu's parameters *replace* Bitcoin's mainnet parameters
in `CMainParams` (`src/kernel/chainparams.cpp:108`), and Treeneesu's test
parameters replace regtest's in `CRegTestParams` (:587). Bitcoin's testnet /
testnet4 / signet classes are **deleted**. Result: the built binary *cannot*
connect to Bitcoin at all — there is no Bitcoin chain left in it to connect to.
That is the strongest possible independence guarantee, and the smallest,
most reviewable diff.

Rejected alternative: adding Treeneesu as a brand-new chain type alongside
Bitcoin (`-chain=treeneesu`). It touches the `ChainType` enum, CLI parsing,
RPC, wallet loading and dozens of tests, and leaves live Bitcoin parameters —
including its seed nodes — inside the binary. Bigger risk, weaker separation.

Consequence to accept: inside this fork, `getblockchaininfo` will still call
the Treeneesu chain `"main"` and the test chain `"regtest"`. Renaming those
strings is cosmetic Phase 3 work, optional, and does not affect identity.

---

## 2. Identity and naming

| Item | Proposal | Notes |
|---|---|---|
| Project / coin name | **Treeneesu** | set by Muteeb |
| Ticker ◆ (D2) | **TNSU** (alternatives: TNEE, TRSU) | See collision note below |
| Smallest unit | 1 TNSU = 100,000,000 base units (unchanged `COIN`, `src/consensus/amount.h`) | subunit name provisional: "nesu" |
| Client / user-agent | UA name `Satoshi` → `Treeneesu` (`src/clientversion.cpp:22`) | branding, non-consensus |
| Binaries | `treeneesud`, `treeneesu-cli`, `treeneesu-tx`, `treeneesu-wallet`, `treeneesu-util` | build-system rename, non-consensus |
| Data directory | `~/.treeneesu` (was `~/.bitcoin`, `src/common/args.cpp:886`) | straightforward |
| Config file | `treeneesu.conf` (was `bitcoin.conf`, `src/common/args.cpp:35`) | straightforward |
| Version | fork version starts at `0.1.0`, CLIENT_VERSION reset in CMakeLists | avoids pretending to be Bitcoin 32.x |

**Ticker collision check (web search, 2026-10-23):** no project using the exact
ticker **TNSU** was found. That is *not* proof of availability — crypto tickers
have no central registry, and anyone can reuse a symbol. Worse, the neighbourhood
is crowded: **TNS** (Token Name Service / Transcodium) and **TNSR** (Tensor) are
live tickers, so TNSU carries a real one-letter confusion risk. This design does
**not** claim TNSU is registered, reserved, or available anywhere.

---

## 3. Money: supply and issuance — Decision D3 ◆ (all PROVISIONAL)

| Parameter | Bitcoin v32 | **Treeneesu proposal** | Where it lives |
|---|---|---|---|
| Initial block subsidy | 50 BTC | **50 TNSU** (unchanged code!) | `src/validation.cpp:1840` `nSubsidy = 50 * COIN` |
| Halving interval | 210,000 blocks | **420,000 blocks** | `consensus.nSubsidyHalvingInterval` (chainparams) |
| Maximum money (validation bound) | 21,000,000 | **42,000,000 TNSU** | `MAX_MONEY`, `src/consensus/amount.h:26` — **consensus change** |
| Decimal places | 8 | 8 (unchanged) | `COIN = 100000000` |

Math (verified by calculation, not asserted): subsidy 50, halving every 420,000
blocks, integer halving in satoshi-style units → total issuance over 33 eras =
**41,999,999.9538 TNSU** — deliberately "just under 42 million", the same effect
Bitcoin has with 21 million. At the §4 block spacing (150 s), one halving era is
420,000 × 150 s ≈ **729 days ≈ 2 years**.

Why this shape: the *only* money-code change is one constant (`MAX_MONEY`) plus
one parameter (halving interval). `GetBlockSubsidy()` itself needs **no edit** —
fewer consensus changes, fewer ways to be wrong.

---

## 4. Proof-of-work and timing — Decision D4 ◆ (PROVISIONAL)

Algorithm: **SHA-256d, Bitcoin's difficulty algorithm unchanged** (`src/pow.cpp`).
We change parameters, we do not rewrite the algorithm.

| Parameter | Bitcoin mainnet | **Treeneesu "main"** | Treeneesu regtest |
|---|---|---|---|
| Target spacing `nPowTargetSpacing` | 600 s | **150 s (2.5 min)** | 600 s (upstream regtest value) |
| Retarget timespan | 14 days | 14 days → **every 8,064 blocks** (`params.h:130`: timespan ÷ spacing) | n/a (no retargeting) |
| Retarget clamp | ×4 / ÷4 per period | unchanged | n/a |
| `powLimit` (easiest allowed difficulty) | `00000000ffff…` | **`00000fffff00…`** (bits `0x1e0fffff`) ◆ | `7fffffff…` (upstream regtest) |
| Min-difficulty blocks | no | no | yes (`fPowAllowMinDifficultyBlocks`) |
| Coinbase maturity | 100 blocks | 100 blocks (unchanged) | 100 |

⚠️ **The honest trade-off in this table:** `powLimit` for Treeneesu main is set
so a laptop CPU expects ~**2²⁰ ≈ 1 million hashes** per block — findable in
seconds-to-minutes. A chain this easy to mine has **no security against history
rewriting** and must never be presented as production-grade. It is set this way
*because* the commission forbids a public/value-bearing network: this is a
private learning chain. If that ever changed (it is out of scope), the entire
difficulty design would need to be redone.

---

## 5. Genesis block — Decision D5 ◆ (text PROVISIONAL)

Constructed in Phase 3 exactly the way upstream does it
(`CreateGenesisBlock(...)` inside `CMainParams`, with in-code asserts on the
resulting hash and merkle root). Changing *any* field below changes the hash —
that is what makes the chain a different chain.

| Field | Bitcoin (for contrast) | **Treeneesu proposal** |
|---|---|---|
| Timestamp text (`pszTimestamp`) | "The Times 03/Jan/2009 Chancellor…" | **"Treeneesu 23/Oct/2026 — a learning chain with no monetary value"** ◆ |
| Block time (`nTime`) | 1231006505 | Unix time of the Phase 3 build day, fixed in code |
| Bits (`nBits`) | `0x1d00ffff` | **`0x1e0fffff`** (per §4) |
| Nonce (`nNonce`) | 2083236893 | **ground at implementation time** — we iterate nonces until the block hash meets the target (~2²⁰ expected tries); the found nonce + resulting hash are recorded and asserted in code |
| Version | 1 | 1 |
| Reward | 50 BTC | 50 TNSU (coinbase, unspendable in practice like Bitcoin's genesis) |

Regtest genesis gets the same treatment with its own timestamp text, time,
nonce 2-style trivial difficulty (bits `0x207fffff`, upstream regtest value).

---

## 6. Network identity — Decision D6 ◆ (PROVISIONAL)

| Item | Bitcoin mainnet | **Treeneesu main** | **Treeneesu regtest** | Where |
|---|---|---|---|---|
| Magic bytes `pchMessageStart` | `f9 be b4 d9` | **`a7 3e 5c 91`** | **`b1 c2 d3 e4`** (replaces regtest's `fa bf b5 da`) | chainparams |
| P2P port | 8333 | **29333** | **29444** | chainparams |
| RPC port (default = P2P − 1 convention) | 8332 | **29332** | **29443** | `src/chainparamsbase.cpp` |
| DNS seeds `vSeeds` | 7 Bitcoin seed hosts | **EMPTY — deleted** | empty | chainparams:168-174 |
| Fixed seeds `vFixedSeeds` | Bitcoin IP list | **EMPTY — deleted** | empty | chainparams:184 |

Checks done: all five upstream magics and ports (8333/18333/48333/38333/18444)
listed and avoided; candidate ports 29333/29332 produce no port usage anywhere
in the source tree (only unrelated digit substrings inside crypto test data).
Ports and magic bytes are **not registered with any authority** — they are
simply values no other chain in this codebase uses. With seeds deleted and the
port/magic changed, two Treeneesu nodes find each other only by explicit
`-connect` / `-addnode` — which is exactly right for a private network.

Peers reject messages with the wrong magic at the protocol level, so a
Treeneesu node and a Bitcoin node cannot even complete a handshake.

---

## 7. Addresses and keys (wallet-visible identity)

| Item | Bitcoin | **Treeneesu proposal** ◆ (D7) | Where (`CMainParams`) |
|---|---|---|---|
| Base58 pubkey prefix | 0 (`1…` addresses) | **65** (addresses begin with `T`) | `base58Prefixes[PUBKEY_ADDRESS]` |
| Base58 script prefix | 5 (`3…`) | **22** | `[SCRIPT_ADDRESS]` |
| WIF secret prefix | 128 | **193** (= 65 + 128, the upstream pattern) | `[SECRET_KEY]` |
| Extended pubkey | `0488B21E` (`xpub`) | **`02FE6D4F`** (arbitrary, unregistered) | `[EXT_PUBLIC_KEY]` |
| Extended privkey | `0488ADE4` (`xprv`) | **`02FE6D47`** | `[EXT_SECRET_KEY]` |
| Bech32 HRP | `bc` (`bc1…`) | **`tnsu`** (`tnsu1…`) | `bech32_hrp` |
| Bech32 regtest HRP | `bcrt` | **`tnsurt`** | regtest params |
| Silent-payments HRP | `sp` | `tsp` (kept distinct; feature unused in our scope) | `silent_payments_hrp` |

Notes: prefix 65 is also used by another network (Tron) for a different
encoding — a human-confusion note, not a technical conflict, since Base58Check
payloads and bech32 HRPs differ. BIP32 extended-key bytes and a SLIP-0044 coin
type are **not registered** for Treeneesu and this doc does not pretend
otherwise. Address prefixes are wallet/encoding-layer — important for identity,
but they are **not** consensus rules: changing them does not change which
blocks are valid.

---

## 8. The hidden Bitcoin-identity checklist (why rebranding alone fails)

These are the items a logo-and-name fork misses. All verified present in
`CMainParams` at v32.0; Phase 3 must handle **every one**:

1. `script_flag_exceptions` (chainparams:115-117) — script-rule exceptions keyed
   to two *Bitcoin block hashes*. They can never occur on our chain; keeping
   them is dead weight that proves the code still thinks it's Bitcoin. **Delete.**
2. `consensus.BIP34Hash` (:120) — hash of Bitcoin block 227,931. Our chain has
   no such block. **Set BIP34Height = 1 and BIP34Hash = our genesis hash**,
   mirroring upstream regtest's proven pattern (activations at height 1,
   SegwitHeight = 0). Same for BIP65/66/CSV heights: Bitcoin's 388381/363725/
   419328 become **1**; Segwit **0** — every modern rule active from the start.
3. `consensus.nMinimumChainWork` (:141) — Bitcoin's accumulated work. **Reset**
   to the work of our genesis block (effectively ~0 at our difficulty).
4. `consensus.defaultAssumeValid` (:142) — a Bitcoin block hash at height
   966,143. **Set to zero** (disabled) until our chain ever earns one.
5. `m_assumeutxo_data` (:189-…) — snapshots of Bitcoin's UTXO set at heights
   840,000/880,000. Meaningless and dangerous here. **Delete.**
6. `chainTxData` (:222) — Bitcoin mainnet transaction-count statistics used
   for sync estimation. **Replace** with genesis-only values.
7. DNS + fixed seeds (§6). **Delete both.**
8. Testnet/testnet4/signet parameter classes. **Delete** (per D1) so no Bitcoin
   network remains reachable; their unit/functional test fixtures go with them.
9. `UA_NAME "Satoshi"` (`src/clientversion.cpp:22`) and version/help strings
   naming Bitcoin. **Rename** (branding; non-consensus but identity-visible in
   every peer handshake via the user-agent).

---

## 9. What does NOT change

- **Transaction validation** (`src/validation.cpp`, `src/consensus/tx_verify.cpp`):
  same checks, same script engine, same sighash rules. Only the money-supply
  bound and activation heights around it change.
- **Block validation**: same `CheckBlock` / `ConnectBlock` path; our blocks are
  validated by the same code that validated Bitcoin's in Phase 1.
- **Wallet**: same SQLite descriptor wallet code; it just encodes addresses
  with §7's prefixes and talks to our datadir.
- **Peer networking**: same transport (including BIP324), same message set.
  Only magic/port/seeds — the *identity* of the network — change.
- **Mining**: same `BlockAssembler` (`src/node/miner.cpp`) and
  `generatetoaddress` flow we exercised in the Phase 1 regtest demo.

## 10. Change classification (the §"straightforward vs consensus" answer)

**Straightforward (config/branding, low risk, no consensus effect):**
datadir & config filename, binary names, UA/version strings, docs, removing
GUI references. P2P/RPC ports and magic bytes sit in chainparams but are
network-identity constants, not validity rules.

**Consensus-critical (C++ parameter/constant changes — each needs its own
small patch + tests, per the commission's rules):**
genesis block (all fields + asserts), `powLimit`, `nPowTargetSpacing`,
`nPowTargetTimespan` (via retarget period), `nSubsidyHalvingInterval`,
`MAX_MONEY`, activation heights + `BIP34Hash`, `nMinimumChainWork`,
`defaultAssumeValid`, assumeutxo removal, script-exception removal.

**Encoding/wallet-layer (not consensus, still needs tests):**
base58 prefixes, extended-key bytes, bech32 HRPs — expect upstream
`key_io_tests` and address fixtures to need Treeneesu values.

## 11. Test plan baked into Phase 3 (preview)

Per patch: rebuild → `test_bitcoin` must stay at 827/827-equivalent (minus
deleted-testnet suites, plus new Treeneesu cases: genesis hash assert,
`MAX_MONEY` amount tests, subsidy schedule test at era boundaries, pow
retarget test at 150 s spacing). Then the Phase 1 regtest demo re-run against
Treeneesu regtest, a restart-persistence check, a two-node `-addnode` sync
check, and negative tests (Bitcoin-magic peer rejected; block with wrong
subsidy rejected; overspend rejected). Phase 4 then re-verifies independence
end-to-end. Details when we get there — no step in this section is approved
by approving the parameters above; each patch gets its diff shown first.

## 12. Known limitations of this design

- Difficulty is intentionally trivial (§4) → zero rewrite-resistance.
- No seed infrastructure → nodes pair manually; fine for a private network.
- Ticker/prefixes/ports are unregistered proposals (§2, §6, §7).
- Keeping `-chain=main`/`regtest` string names (D1 consequence).
- Treeneesu inherits Bitcoin's known design trade-offs wholesale (UTXO model,
  1 MB-ish weight limits, fee market) — this design forks the implementation,
  it does not attempt to improve on Bitcoin.

## 13. Decisions needed from Muteeb (approve / amend each)

- **D1** Approach: replace-main (recommended) — §1
- **D2** Ticker: TNSU / TNEE / TRSU / other — §2
- **D3** Supply: 42M cap, 50 TNSU initial, 420k-block halvings — §3
- **D4** Timing & difficulty: 150 s spacing, 14-day retarget, easy powLimit — §4
- **D5** Genesis timestamp text — §5 (exact wording)
- **D6** Magic bytes + ports 29333/29332, regtest 29444/29443 — §6
- **D7** Address set: prefix 65 (`T…`), HRP `tnsu` — §7
- **D8** Activations from height 1/0 (all modern rules on from genesis) — §8.2

---

## Amendment 2026-10-23 — D4 powLimit corrected (owner decision: Option A)

The provisional powLimit above (bits `0x1e0fffff`, target ≈ 2^236) proved
**defective**: pow_tests' sanity check enforces powLimit <
2^256/(4·nPowTargetTimespan) ≈ 2^233.8, because CalculateNextWorkRequired
multiplies the target by the (clamped) actual timespan in 256-bit
arithmetic; 2^236 × up-to-2^22.2 overflows at the first retarget (block
8064). The owner selected Option A on 2026-10-23:

- **powLimit bits: `0x1e01ffff`** (target `000001ffff00…`, ≈ 2^233, margin
  ≈ 0.79 bits under the exact bound — sufficient because the 4× timespan
  clamp makes the bound a hard maximum, not an estimate).
- Expected work per block ≈ 2^23 ≈ 8.4M hashes.
- Genesis re-ground (identical coinbase): nonce 26434925, hash
  00000091bddca562e9b5a2c98b31e5e5c831ffc015c6fd8853ef18d6df22dfee.
  See genesis/GENESIS-VERIFICATION.md, Amendment section.
- Rejected alternatives: B (0x1d3fffff, more margin, ~8× slower mining —
  unnecessary given the clamp argument) and C (keep defective value).
