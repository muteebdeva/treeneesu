# Mission 8a — Public testnet plan (PLAN ONLY — nothing here is executed)

A public testnet is a separate Treeneesu chain that anyone can join, with
coins that are worthless by definition. This plan exists so the owner can
approve or reject it with full information. **No step runs without explicit
owner approval.**

## Prerequisites (all mandatory)
1. BLOCKERS B1 resolved (powLimit fixed, genesis re-ground, everything
   re-verified). A testnet launched on the defective parameters would break
   at block 8064 in public — the worst possible first impression.
2. B2 decided: the testnet should be a proper chain parameter set (its own
   genesis/magic/ports/HRP, e.g. `tnsut` style test HRP), replacing the
   placeholder testnet slots rather than reusing Bitcoin's.
3. Owner approves this plan, the seed operators, and the public wording.

## Design (proposed)
- **Chain**: new `CTestNetParams`-style parameter set: own genesis (message
  marking it as a test chain), own magic, P2P/RPC ports distinct from main
  (proposal: 39333/39332), bech32 HRP `tnsurt`-style distinct prefix, same
  monetary schedule as main so behavior mirrors it, low powLimit (after the
  B1 fix values are chosen) so a laptop can mine test coins.
- **Seeds**: 2–3 small always-on nodes run by named volunteers/owner; DNS
  seed optional and only after the static seeds prove stable. All seed
  operators are listed publicly.
- **Faucet**: a simple web form or chat command dripping small amounts;
  rate-limited; big red "these coins are worthless" notice.
- **Explorer**: optional; any free open-source explorer instance. Skip if it
  costs money (₹0 budget rule).
- **Docs**: one page — how to build, how to connect (`-chain=test` +
  `-addnode` list until seeds work), how to get test coins, abuse contact,
  shutdown procedure.

## Rollout steps (each gated)
1. Owner approves final parameters → implement as its own patch, full test
   pass + two-node demo on the test chain.
2. Two seed nodes up (owner-run first), cross-checked genesis + sync.
3. Faucet live with worthless-coins wording reviewed by owner.
4. Announcement draft → owner approves exact text → only then publish.
5. First-week monitoring: chain height, peer count, any consensus warnings
   in seed logs reviewed daily.

## Kill criteria (stop and announce shutdown if any occur)
- Any consensus divergence between seeds (different best-chain hashes at
  the same height that doesn't resolve).
- Anyone marketing test coins as valuable or selling them.
- Abuse (spam/DoS) that the operators can't mitigate with built-in tools.

## Explicitly out of scope
No mainnet, no listings, no price, no promises of future value, no paid
infrastructure. Budget remains ₹0.
