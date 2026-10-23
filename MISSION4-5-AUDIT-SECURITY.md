# Missions 4 & 5 — Implementation Audit and Practical Security Review

Scope: all Treeneesu changes relative to Bitcoin Core v32.0 (commit 465dde27):
Patch 1 (committed, 5790ce2), Patch 2a (uncommitted), Mission 2 test repairs
(uncommitted). This is a self-review by the implementing agent — it is NOT a
professional security audit, and no statement here should be read as one.

## Mission 4 — Independent-chain requirements checklist

### Chain identity
| Requirement | Status | Evidence |
|---|---|---|
| Own genesis block | ✔ | Hash 000008c949ab…015b6; ground and verified pre-change (GENESIS-VERIFICATION.md); both demo nodes report it |
| Genesis coinbase unspendable | ✔ | By construction (genesis outputs never enter the UTXO set, validation.cpp) |
| Own network magic | ✔ | a7 3e 5c 91 (main); cannot peer with Bitcoin (magic + genesis both differ) |
| Own P2P/RPC ports | ✔ | 29333 / 29332 (main) |
| No Bitcoin DNS/fixed seeds | ✔ | CMainParams clears both (chainparams.cpp, design D6); nodes peer only via -addnode/-connect |
| Own address formats | ✔ | base58 65/22/193, bech32 HRP `tnsu`, ext keys 02FE6D4F/02FE6D47; demo produced `tnsu1…` addresses; full key_io/descriptor test coverage passes |
| Own data directory & config | ✔ | `.treeneesu` / `treeneesu.conf` (Patch 1), verified live |
| Own user agent | ✔ | `/Treeneesu:32.0.0/` (Patch 1), verified live |
| BIP324 transport bound to new magic | ✔ | HKDF salt includes magic; vectors regenerated + suite passes; functional p2p_v2_transport passes |
| No stale assumevalid/checkpoints | ✔ | defaultAssumeValid zeroed; assumeutxo data deleted; v32 has no checkpoint map (removed upstream) |
| Minimum chain work sane | ✔ | Set to genesis work (0x100001); two-node sync works |

### Monetary policy (design D3)
| Requirement | Status | Evidence |
|---|---|---|
| Cap 42,000,000 TNSU | ✔ | MAX_MONEY in amount.h; MoneyRange enforced by CheckTransaction (tx_invalid vectors at cap+ε verified) |
| Subsidy 50, halving 420,000 | ✔ | chainparams; subsidy_limit_test verifies exact total issuance 41,999,999.9538 TNSU |
| 150 s spacing, 14-day retarget (8,064 blocks) | ✔ params set | Retarget *correctness* is compromised by the powLimit defect below until the owner decides |

### Consensus / deployments (design D8)
- BIP34/65/66/CSV at height 1, segwit at 0, BIP34 hash = Treeneesu genesis ✔ set in 2a.
- script_flag_exceptions (Bitcoin-specific) deleted ✔.
- Headers pre-sync params: left at upstream values (documented deviation from
  Phase 2 design notes); harmless at current chain work scale, flagged for
  the pre-mainnet checklist.

### Known incompleteness (not defects of what exists — unfinished scope)
1. **powLimit defect (OPEN, owner decision pending)** — bits 0x1e0fffff
   violates the retarget overflow invariant; first retarget (block 8064)
   would miscompute difficulty. See MISSION2-CHANGELOG.md.
2. Patch 2b (regtest replacement: own genesis/magic/ports/HRP for the
   developer chain) — NOT DONE. Regtest is still Bitcoin's. Scope was frozen
   by the mission; functional tests therefore exercise Bitcoin regtest.
3. Patch 2c (delete testnet/testnet4/signet params) — NOT DONE. Those chain
   parameter sets still exist and still carry Bitcoin seeds. They cannot
   affect the Treeneesu main chain, but a "fully independent" release should
   remove them (frozen scope; needs owner approval).
4. Binary names (`bitcoind`, `bitcoin-cli`) and the startup banner still say
   Bitcoin — cosmetic rebrand remainder of Patch 1, deliberately deferred.
5. GUI (qt) strings/branding untouched (GUI not built in this environment).

## Mission 5 — Practical security review of the custom changes

### What the changes touch
Production-code changes are limited to: identity strings (Patch 1), chain
parameters + MAX_MONEY (Patch 2a). No new network-facing code, no new parsers,
no cryptography changes. BIP324, mempool, validation, wallet logic are
upstream code with upstream test coverage, all passing.

### Findings
1. **powLimit overflow (severity: high for any real deployment; none for
   local testing below height 8064).** Detailed in the changelog. Must be
   fixed before any network others rely on.
2. **Low absolute PoW (by design).** Even after the powLimit fix, difficulty
   ≈ 2^23 hashes/block means any CPU can rewrite the chain cheaply. Treeneesu
   must never be presented as secure against reorg attacks; suitable only as
   a learning/test network. (Design intent; recorded so it is never lost.)
3. **Ext-key version bytes are unregistered** (02FE6D4F/02FE6D47). Collision
   with another chain's registered prefixes is possible in principle; impact
   is wallet-import confusion, not theft. Documented in the design file.
4. **No seed nodes (by design D6).** Eliminates seed-poisoning surface;
   cost: manual peering only, higher eclipse risk for a lone node joining
   via a single -addnode. Acceptable for a private learning chain; a public
   testnet must add operator-run seeds deliberately (Mission 8 gate).
5. **Test-fixture integrity.** Mission 2 changed many test constants. Each
   change is payload-preserving or recomputed with a control-verified
   independent implementation (BIP324, descriptor checksums/hashes via dual
   Python+C++-oracle agreement, subsidy total computed two ways). No
   assertion was weakened; the full suite passes except pow_tests (defect
   #1's own test).
6. **Secret handling.** No private keys/seeds exist for this project beyond
   throwaway local test wallets in /tmp. The GitHub PAT pasted in chat on
   2026-10-23 was never used or stored (revocation still recommended).
7. **Upstream hygiene.** The tree keeps upstream copyright/license notices;
   the only removed upstream data are Bitcoin's chain-specific constants
   (seeds, assumeutxo snapshots, script-flag exceptions) whose retention
   would have been actively wrong for an independent chain.

### Verification evidence behind these claims
- Full unit suite (152 suites): all pass except pow_tests (4 errors, defect #1).
- Two-node main-chain demo: genesis identity, peering, 109 real-PoW blocks,
  sync, tx propagation + confirmation, exact balances, restart recovery —
  `logs/twonode-demo-final.log`, script `twonode-demo.sh`.
- Functional subset (incl. BIP324 v2 transport, segwit, wallet): all pass.
- ASan build + subset run: see logs/asan-* (in progress at time of writing).
