# Security & launch checklist

Full review: `../MISSION4-5-AUDIT-SECURITY.md`. This is the operational
summary. Treeneesu is a learning chain — checking these boxes makes a
*testnet* safer; nothing makes this design safe for real value.

## Before any public testnet
- [ ] powLimit defect fixed, genesis re-ground, all vectors/tests re-verified.
- [ ] Owner approves the testnet plan (`../TESTNET-PLAN.md`) explicitly.
- [ ] At least 2–3 independently operated seed nodes planned (the chain has
      none by design today); peers can find the network without trusting one
      person's machine.
- [ ] Faucet/test-coin policy written down: coins are worthless, never sold,
      never marketed as an investment.
- [ ] Public wording reviewed: no "investment", no price talk, no
      production-readiness claims (project rule).
- [ ] Abuse contact and a shutdown procedure published with the testnet.

## Never (hard project rules)
- No mainnet launch or real-value deployment without the owner's explicit
  human approval gate (Mission 8).
- No token sale, no spending money on infrastructure, no paid services.
- No publishing/pushing to remotes without explicit approval.
- No presenting the self-review as a professional security audit.

## Standing risks to disclose wherever Treeneesu is described
- Mining difficulty is intentionally tiny: history can be rewritten by one
  ordinary computer. The chain proves *mechanics*, not *security*.
- No checkpoints/assumevalid anchors beyond genesis work: a fresh node
  trusts the longest-work chain it can find, and with no seeds it trusts
  whoever it is manually connected to (eclipse risk).
- Ext-key prefixes are unregistered; importing a Treeneesu xpub into
  software that doesn't know them may confuse or mislabel funds.
