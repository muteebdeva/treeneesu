#!/usr/bin/env python3
"""Derive a defensible nMinimumChainWork value for a Treeneesu release.

Implements the maintenance rule in THREAT-MODEL.md §6: the value is an
OUTPUT of the real chain's state, never an invented constant.

Usage:
  min-chain-work.py --cli "bitcoin-cli -datadir=/path -rpcport=29332" \
      [--safety-blocks 100]

It reads the node's tip (getblockchaininfo: blocks, bestblockhash,
chainwork), walks back --safety-blocks blocks, and prints the
nMinimumChainWork constant to use (the chainwork AT that earlier
height), together with the full provenance record that must be copied
into the release notes. It changes nothing itself.
"""
import argparse, json, subprocess, sys

def rpc(cli, method, *params, raw=False):
    out = subprocess.run(cli.split() + [method, *map(str, params)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"RPC {method} failed: {out.stderr.strip()}")
    if raw:  # e.g. getblockhash returns a bare hash, not JSON
        return out.stdout.strip().strip('"')
    return json.loads(out.stdout)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", required=True, help="bitcoin-cli invocation prefix")
    ap.add_argument("--safety-blocks", type=int, default=100,
                    help="set the value at tip minus this many blocks")
    a = ap.parse_args()

    info = rpc(a.cli, "getblockchaininfo")
    tip_h, tip_hash, tip_work = info["blocks"], info["bestblockhash"], info["chainwork"]
    if tip_h < a.safety_blocks:
        sys.exit(f"chain too short: tip {tip_h} < safety margin {a.safety_blocks}")
    anchor_h = tip_h - a.safety_blocks
    anchor_hash = rpc(a.cli, "getblockhash", anchor_h, raw=True)
    hdr = rpc(a.cli, "getblockheader", anchor_hash)
    value = hdr["chainwork"]  # cumulative work up to and including anchor block

    print("nMinimumChainWork derivation (copy into the release notes):")
    print(f"  node tip:            height {tip_h}  {tip_hash}")
    print(f"  node tip chainwork:  0x{tip_work}")
    print(f"  safety margin:       {a.safety_blocks} blocks")
    print(f"  anchor block:        height {anchor_h}  {anchor_hash}")
    print(f"  VALUE (chainwork at anchor): uint256{{\"0x{value}\"}}")
    print("  rule: THREAT-MODEL.md section 6 — value is read from the real")
    print("        designated chain; never invent or reuse across chains.")

if __name__ == "__main__":
    main()
