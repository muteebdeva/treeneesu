# Release runbook & checklist

## Release checklist (all boxes must be checked, in order)
1. [ ] Owner decision recorded for every open consensus item (see BLOCKERS.md).
2. [ ] Clean-checkout build from scratch succeeds (fresh clone → configure →
       build → binaries present). NOT YET DONE for the RC (see TEST-SUMMARY).
3. [ ] Full unit suite passes with zero unexplained failures.
4. [ ] Functional test subset passes (COMMANDS.md list).
5. [ ] Two-node demo passes end-to-end (`twonode-demo.sh`, exit 0).
6. [ ] Address/key test vectors verified against a second implementation or
       independent check (done for BIP324/descriptor/BIP32 in Mission 2 —
       redo after any parameter change).
7. [ ] Genesis hash in README, docs, and code agree (search the tree for the
       hash string).
8. [ ] No secrets in the tree: `git grep -i "ghp_\|api_key\|seed" ` reviewed;
       no wallet files, no `.env`, no datadirs committed.
9. [ ] Version string and release notes updated; known-limitations section
       included (low PoW security, no seeds, test-only status).
10. [ ] Owner approval for: commit, tag, any push, any announcement —
        each separately.

## Cutting a release candidate (local only)
```bash
git status            # review every modified file against MISSION2-CHANGELOG
git diff --stat       # 21 files at RC-prep time (3 production, 18 test/harness)
```
Do NOT commit, tag, or push without explicit owner approval (project rule).

## Operating a local node
- Start/stop and CLI examples: `COMMANDS.md`.
- Data lives in the `-datadir` you pass (default `~/.treeneesu`).
- Backups: the only irreplaceable file is `wallet.dat` inside
  `<datadir>/wallets/<name>/`. Test wallets in this project hold valueless
  coins on a local chain — treat them as disposable.
- Upgrading: stop the node (`bitcoin-cli … stop`), replace binaries, start.
  Never copy a live `chainstate/` directory.

## Incident basics
- Node won't start: read the tail of `<datadir>/debug.log` first; the last
  20 lines almost always name the problem (port in use, corrupt settings,
  locked datadir from a crashed instance).
- Chain disagreement between two local nodes: compare `getblockhash 0` and
  `getbestblockhash`; a genesis mismatch means different binaries/params —
  do not try to "fix" by deleting random files; identify the wrong node,
  stop it, and (for disposable test chains) delete its datadir.
