# Treeneesu — Threat Model & Security Design

Written 2026-10-23 as the first artifact of the production-readiness
engineering phase. This document defines what Treeneesu **is**, what it
is **not**, and what security it can and cannot claim. Engineering
decisions in this phase (and the updated gate statuses) trace back to
the definitions here. If this document and any other project document
disagree about scope, this document governs.

## 1. What Treeneesu is

Treeneesu is a **standalone, Bitcoin Core–derived experimental
blockchain** built for learning and protocol experimentation:

- Independent chain: own genesis, network magic `a7 3e 5c 91`, ports
  29333/29332, address formats, 42M TNSU supply cap, 50 TNSU subsidy
  halving every 420,000 blocks, 150-second target block interval,
  8,064-block (14-day) difficulty retarget using Bitcoin's algorithm
  unchanged.
- All consensus machinery (validation, PoW check, retarget algorithm,
  chain selection, mempool, P2P, wallet) is unmodified Bitcoin Core
  v32.0 code. The complete Treeneesu-specific production difference is
  5 files (see PRODUCTION-DIFF.patch).
- **Its coins have no monetary value. It is not a payments network, not
  an investment, and not a store of value.** This is stated in the
  genesis block itself, the README, and every release document.

## 2. What Treeneesu is not

- It is **not** a production cryptocurrency. There is no mining
  ecosystem, no exchange, no user funds, and no service depending on
  it. Nothing in this phase changes that, because the missing
  ingredient — a sustained, independently distributed mining
  ecosystem — cannot be created by software changes (see §5).
- It is not a fork *of the Bitcoin network*: it shares code, not a
  chain. It cannot transact with Bitcoin, and Bitcoin tooling that
  assumes Bitcoin's chain parameters must not be pointed at it (see
  the F-05 disposition for the binary's auxiliary chain classes).

## 3. Assets and security goals

| Asset | Goal |
|---|---|
| Source code integrity | Anyone can verify what the code does: tiny auditable diff, licence-clean, secret-free. |
| Chain-rule correctness | Every honest node reaches the same consensus; issuance never exceeds the modelled schedule (41,999,999.9538 TNSU). |
| Operator safety | Running a node must not endanger the operator's machine beyond the known risks of running Bitcoin Core–class software (documented defaults, localhost RPC). |
| Experimental-chain continuity | The demo/test chains should behave correctly (sync, retarget, recovery) so experiments produce trustworthy results. |
| User funds | **Out of scope.** There are none, and the design does not protect hypothetical funds (§5). Any use with value is a misuse. |

## 4. Attacker model

For the experimental chain, the assumed attacker is:

- A network participant who can run modified nodes, send malformed
  messages, mine blocks, and attempt reorganizations, with commodity
  resources (a few CPUs/GPUs).
- **Not** assumed: nation-state resources, zero-days in upstream
  Bitcoin Core, or physical access to operators' machines. Treeneesu
  inherits upstream's posture for those and adds nothing.

For completeness, the *hypothetical* value-bearing attacker (used only
to evaluate F-01/F-03) is anyone with ≥ one modern CPU: at the current
difficulty (~2²³ hashes/block), that is already sufficient to rewrite
the chain (see §5). No confirmation policy fixes this (§5.2).

## 5. Proof-of-work security — the honest analysis (F-01)

### 5.1 The numbers

- powLimit bits 0x1e01ffff ⇒ expected work per block ≈ 2²³ hashes.
  A single CPU core with SHA-NI (≈3–7 MH/s) produces a block in
  ~1–3 seconds of hashing; the 150 s interval exists only because no
  one is mining continuously.
- Total work to rewrite N blocks ≈ N × 2²³ hashes — e.g., rewriting a
  full day of blocks (576) costs ≈ 2^32.2 hashes ≈ **15–30 minutes on
  one CPU core**. `nMinimumChainWork` is one block (§6).
- Rented-hashpower framing is unnecessary: the attack is free with
  hardware the attacker already owns.

### 5.2 Why "just raise the difficulty" is not a fix

Raising powLimit's difficulty (lowering the target) without a mining
ecosystem produces a chain that (a) still has no security — the same
single CPU is merely the *only* miner instead of a sufficient
attacker; (b) cannot start: block production becomes slower than the
target interval by orders of magnitude until the retarget algorithm
eases difficulty back down over multiple 8,064-block periods, which at
a too-high initial difficulty can take geological time (the retarget
can only divide by 4 per period); and (c) if done on the existing
genesis, changes consensus identity — a new genesis block means a
**new chain**, invalidating every existing test artifact tied to the
current parameters.

Security in proof-of-work comes from *aggregate honest hashpower
exceeding attacker hashpower*, not from the difficulty constant.
Difficulty follows hashpower via the retarget; it does not create
hashpower. Bitcoin is secure because of its miners, not because
0x1d00ffff is a magic number.

### 5.3 Confirmation-risk model (for the hypothetical case)

With attacker hashpower share *q* and honest share *p = 1−q*, the
probability an attacker ever rewrites a transaction buried under *z*
confirmations is (q/p)^z (Bitcoin whitepaper §11). On today's
Treeneesu, an attacker with one CPU against ~zero honest hashpower has
q ≈ 1, so the probability is ≈ 1 **for every z**. There is no safe
confirmation count. Any document or UI implying otherwise would be a
false security claim, and none may be written.

### 5.4 Disposition

- **F-01 remains OPEN for any value-bearing scope, permanently, for
  this chain.** This is a design property, not a bug to patch.
- For the chain's actual scope (experimentation), ~2²³ is a *feature*:
  blocks are cheap to produce in tests, and the retarget dynamics are
  fully exercised at the 8,064-block boundary (F-02 soak).
- A future value-bearing successor chain is a **new project**: new
  genesis ground at a Bitcoin-class difficulty, a launch plan whose
  precondition is committed independent hashpower, `nMinimumChainWork`
  set from real accumulated work (§6), and its own audit. The concrete
  re-parameterization procedure and measured grind costs are recorded
  in F01-POW-ANALYSIS.md so the path is engineered, not hand-waved.

## 6. Minimum chain work — design (F-03)

`nMinimumChainWork` exists so a node in initial sync does not waste
work on low-work forks before it has seen the real chain. Its correct
value is a *release-engineering output*, not a constant to invent:

- At genesis, the only non-fabricated value is the genesis block's own
  work: 0x800040. **The audited value is therefore correct for a
  pre-launch chain**, and raising it now to an arbitrary number would
  be checklist theatre (it would also brick fresh nodes if set above
  the real chain's work).
- Maintenance rule (implemented as `tools/min-chain-work.py` and
  documented in RELEASE-PROCESS.md): for any release intended to serve
  a live network, the maintainer reads the designated chain's tip
  `chainwork` from a fully synced node at a named height, sets
  `nMinimumChainWork` to that value minus a small safety margin, and
  records height, tip hash, and value in the release notes. Upstream
  Bitcoin Core follows exactly this practice per release.
- Limitation, stated plainly: at Treeneesu's work scale this mechanism
  is a sync-optimization, not a security boundary (see §5.1).
  Distinguishing "the intended chain" today is by genesis hash —
  operators must compare `getblockhash 0` against the published value
  (README, TESTNET-GUIDE.md).

## 7. Network trust assumptions (F-04)

- There is no bootstrap infrastructure. Nodes peer only by explicit
  `-addnode`/`-connect`. This is a deliberate containment property for
  an experimental chain (it cannot accidentally join or pollute
  Bitcoin's networks — main-class magic/ports are unique, seeds
  deleted), and simultaneously the reason no public network can form.
- A public testnet requires owner-provisioned infrastructure (seed
  nodes + a DNS seed under a domain the owner controls). The deploy
  package in `deploy/` specifies it exactly; provisioning it is an
  owner action (hosting accounts, DNS, and cost are the owner's), and
  no hostname is claimed to exist until it does.

## 8. Confirmation & usage policy (normative for all docs)

1. TNSU balances in any demo/test are **play numbers**. No document
   may describe them as payments of value.
2. No confirmation count may be presented as making a Treeneesu
   transaction "safe" or "final" in an economic sense.
3. Wallets holding keys for Treeneesu addresses must be treated as
   test wallets; the same seed must never secure anything of value.
4. RPC must stay bound to localhost unless the operator has set
   authentication and understands the exposure (TESTNET-GUIDE.md §3).

## 9. Residual-risk statement

Even with every completable gate in this phase closed, the following
remain true and are accepted by scope, not solved: no independent
human reviewer has signed the diff (Gate D stays partially open until
one does); upstream Bitcoin Core itself carries undiscovered bugs as
any large codebase does; and the chain's security equals the honesty
of whoever chooses to mine it. The release decision that follows from
this threat model is recorded in FINAL-REPORT.md.
