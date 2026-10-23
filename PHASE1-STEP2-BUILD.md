# TREENEESU — Phase 1, Step 2: Pin, Dependencies, Build — Log
Date: 2026-10-23 (Asia/Kolkata) · Approved by Muteeb via options widget 13:00 IST
Result: ✅ BUILD SUCCEEDED — evidence below. No source files edited.

## 1. Pin to release tag v32.0
```
git fetch --depth 1 origin tag v32.0
git checkout v32.0
```
Result: HEAD 465dde277447e2f11e01bea09d2a094d7fb6ef45 ("[32.0] Finalize", 2026-10-21),
CMakeLists CLIENT_VERSION = 32.0.0, git status clean (0 lines) before and after build
(build/ is upstream-gitignored).

Note: this supersedes the Step 1 inspection baseline (master @152a553, 32.99-dev)
as the build baseline. Architecture file locations are unchanged between the two.

## 2. Dependencies (repo's own doc/build-unix.md at v32.0)
```
apt-get update && apt-get install -y --no-install-recommends \
  build-essential libboost-dev libsqlite3-dev
```
Result: exit 0, duration 12m57s (slow proxy). Verified via dpkg: all INSTALLED —
libboost-dev 1.83, libsqlite3-dev 3.45.1, build-essential. cmake 3.28.3,
g++ 13.3.0, python3 3.12.3 already present. NOT needed at v32: libevent (removed
upstream — confirmed: no Libevent in CMake). Log: logs/step2-apt.log.
Reminder: apt installs do not survive this VM's replacement; rerun this command.

## 3. Configure
```
cmake -B build -DBUILD_GUI=OFF -DENABLE_IPC=OFF \
  -DCMAKE_CXX_FLAGS_RELWITHDEBINFO="-O2 -g0"
```
Result: exit 0 in 25.2s. Summary: wallet ON, test_bitcoin ON, GUI OFF, IPC OFF,
ZMQ OFF, bench OFF, fuzz OFF, compiler GNU 13.3.0, C++20. Log: logs/step2-configure.log.

## 4. Build
```
cmake --build build -j 2
```
Result: **BUILD_EXIT:0**, zero "error:" lines, final line "[100%] Built target test_bitcoin".
BUILD_START 2026-10-23T13:14:19+05:30 → BUILD_END 13:51:09+05:30 = **36 min 50 s**
on this 2-core VM. Log: logs/step2-build.log.

## 5. Binaries verified (build/bin/, 75 MB total)
| Binary | Size | Check |
|---|---|---|
| bitcoind | 18 MB | `--version` → "Bitcoin Core daemon version v32.0" |
| bitcoin-cli | 1.3 MB | `--version` → "Bitcoin Core RPC client version v32.0" |
| bitcoin | 905 KB | present |
| bitcoin-tx | 6.1 MB | present |
| bitcoin-util | 5.7 MB | present |
| bitcoin-wallet | 9.6 MB | present |
| test_bitcoin | 34 MB | present (not yet run) |

## NOT done yet (Phase 1 remainder = proposed Step 3)
- Unit tests (test_bitcoin) not run. No test result is claimed.
- Functional tests not run.
- No regtest node started; no blocks mined; no test transaction made.
- GitHub repo muteebdeva/treeneesu NOT updated with this log yet (needs his OK —
  publishing step). README there still says Step 2 "not started".
