# TREENEESU — Phase 1, Step 1: Repository Inspection Log
Date: 2026-10-23 (Asia/Kolkata) · Inspector: Muse (senior C++ engineer role, per commission)
Scope for this step: READ-ONLY inspection. No source files edited. No build run yet.

## Environment actually checked (this cloud VM)
Command: `cat /etc/os-release; nproc; free -h; df -h ~; git --version; cmake --version; g++ --version; python3 --version`
Actual result:
- OS: Ubuntu 24.04.5 LTS (Noble)
- CPU: 2 cores (AMD EPYC 9D64)
- RAM: 7.7 GiB total — doc/build-unix.md recommends ≥1.5 GB *per parallel compile job*, so build here must use low parallelism (-j1/-j2) and no debug symbols (-g0)
- Disk: 94 GB available (plenty)
- Present: git 2.43.0, CMake 3.28.3, g++ 13.3.0, Python 3.12.3, pkgconf
- Missing on this VM: clang, ccache, and the dev libraries below

## Clone (exact command + result)
```
mkdir -p ~/workspace/treeneesu
cd ~/workspace/treeneesu
git clone --depth 1 https://github.com/bitcoin/bitcoin.git bitcoin-core
```
Result: SUCCESS in 27.5 s, exit 0, 71 MB shallow clone, 3,063 files.
HEAD: commit 152a55397e451fed9c10041bddf01aa6839847d5 (2026-10-22), branch `master`.

## Version, license
- Version in CMakeLists.txt: CLIENT_VERSION 32.99.0, IS_RELEASE=false → this is the
  development tree toward v33, NOT a stable release. For a fork baseline a tagged
  release is safer — decision needed before the build step (see report).
- License: COPYING = MIT License, Copyright (c) 2009-2026 The Bitcoin Core developers.
  MIT permits forking; notices must be preserved (commission rule, and law).

## Build system (from doc/build-unix.md — the repo's own instructions)
Required Ubuntu packages: `build-essential cmake python3 libboost-dev`
Wallet (SQLite): `libsqlite3-dev` · Optional to SKIP: Qt6 GUI, libzmq3-dev, libcapnp-dev
Documented build:
```
cmake -B build
cmake --build build -j N
cmake --install build   # optional
```
Missing deps verified on this VM (dpkg check): libboost-dev, libevent-dev,
libsqlite3-dev, libzmq3-dev, libcapnp-dev, qt6-base-dev — all "missing".

## Test framework (verified counts)
- Unit tests: C++ (Boost.Test), 137 files in src/test/, binary `test_bitcoin` (src/test/CMakeLists.txt)
- Functional tests: Python, 294 scripts in test/functional/, runner: test/functional/test_runner.py
  e.g. `build/test/functional/test_runner.py wallet_basic.py`
- Also: fuzz (test/fuzz), bench (src/bench), lint (test/lint)

## Architecture map (verified file:line, master @ 152a553)
| Concern | File | Notes |
|---|---|---|
| Chain parameters + GENESIS | src/kernel/chainparams.cpp (NOT src/chainparams.cpp — that is now a 169-line wrapper) | CMainParams :108, CTestNetParams :241, CTestNet4Params :350, CRegTestParams :587 |
| Consensus param struct | src/consensus/params.h (163 lines) | nSubsidyHalvingInterval, BIP34/65/66, CSV, Segwit heights |
| Consensus constants | src/consensus/consensus.h; src/consensus/amount.h:26 | MAX_MONEY = 21,000,000 * COIN |
| Block subsidy | src/validation.cpp:1833 GetBlockSubsidy() | starts 50 * COIN, halves every nSubsidyHalvingInterval |
| Block/tx validation | src/validation.cpp (6,424 lines) | ConnectBlock, CheckBlock, GetBlockSubsidy caller :2608 |
| Proof-of-work / difficulty | src/pow.cpp (171 lines) | GetNextWorkRequired :14, CalculateNextWorkRequired :50 |
| Networking | src/net.cpp (4,373), src/net_processing.cpp (6,586) | magic bytes gate peer messages |
| Mining / block assembly | src/node/miner.cpp (BlockAssembler::CreateNewBlock :126), src/node/block_template_manager.cpp | no src/miner.cpp on modern master |
| Wallet | src/wallet/wallet.cpp (4,566 lines) | SQLite descriptor wallets |
| Startup / datadir | src/init.cpp (2,536), src/common/args.cpp:842 GetDefaultDataDir() | Unix default: ~/.bitcoin |

## Bitcoin mainnet identity (the values Treeneesu must NOT reuse)
From CMainParams in src/kernel/chainparams.cpp:
- Genesis: CreateGenesisBlock(1231006505, 2083236893, 0x1d00ffff, 1, 50*COIN)
  hash 000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f (asserted in code)
- Magic bytes: f9 be b4 d9 · P2P port: 8333
- bech32 HRP: "bc" · Base58: PUBKEY 0, SCRIPT 5, SECRET 128, xpub 0488B21E, xprv 0488ADE4
- powLimit 00000000ffff… · retarget 14 days · spacing 10 min (600 s) · halving 210,000
- Plus: DNS seeds (vSeeds) and fixed seeds — a fork must remove/replace these or it will phone Bitcoin peers.

Regtest (our Phase 1 demo target) for comparison: magic fa bf b5 da, port 18444,
HRP "bcrt", powLimit 7fff…, fPowNoRetargeting=true, genesis nonce 2, bits 0x207fffff.

## NOT done in this step (honest status)
- No dependencies installed, no cmake configure, no build, no tests run, no node started.
  Nothing about build/test success is claimed.
- No files in bitcoin-core/ were modified (git status clean at clone).

## Known risks before Step 2 (build)
1. This VM (2 cores) will build slowly — expect well over an hour; use -j2, -g0 flags,
   GUI OFF, IPC OFF to cut scope. Free alternative with more cores: GitHub Codespaces
   (same commands) — user's choice, no account action taken.
2. Building `master` (32.99-dev) means a moving baseline. A tagged release (e.g. latest
   v31/v32 tag) gives reproducible Phase 2 work. Recommendation: pin a release tag.
3. apt installs change the system and do NOT survive VM replacement on this box;
   the dependency-install command is recorded here so it can be re-run anywhere.
