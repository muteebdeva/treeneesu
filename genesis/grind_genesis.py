#!/usr/bin/env python3
"""Treeneesu genesis constructor/verifier.
Replicates Bitcoin Core v32.0 CreateGenesisBlock (src/kernel/chainparams.cpp:37)
byte-for-byte: coinbase tx, merkle root, 80-byte header, double-SHA256, compact target.
"""
import hashlib, json, struct, sys

def dsha(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()

def push_scriptnum(n):
    # CScriptNum minimal encoding
    if n == 0: return b""
    neg = n < 0; a = abs(n); out = bytearray()
    while a: out.append(a & 0xff); a >>= 8
    if out[-1] & 0x80: out.append(0x80 if neg else 0x00)
    elif neg: out[-1] |= 0x80
    return bytes(out)

def push_data(d):
    return bytes([len(d)]) + d if len(d) < 76 else None

def build_coinbase(psz, pubhex, reward_sats):
    script_sig = push_data(push_scriptnum(486604799)) + push_data(push_scriptnum(4)) + push_data(psz.encode())
    script_pub = push_data(bytes.fromhex(pubhex)) + b"\xac"  # OP_CHECKSIG
    tx = struct.pack("<i", 1)                      # version
    tx += b"\x01"                                  # vin count
    tx += b"\x00" * 32                             # prevout hash (null)
    tx += struct.pack("<I", 0xffffffff)            # prevout n
    tx += bytes([len(script_sig)]) + script_sig
    tx += struct.pack("<I", 0xffffffff)            # sequence
    tx += b"\x01"                                  # vout count
    tx += struct.pack("<q", reward_sats)           # value
    tx += bytes([len(script_pub)]) + script_pub
    tx += struct.pack("<I", 0)                     # locktime
    return tx

def compact_target(bits):
    exp = bits >> 24; mant = bits & 0x007fffff
    return mant << (8 * (exp - 3)) if exp > 3 else mant >> (8 * (3 - exp))

def grind(psz, pubhex, ntime, bits, reward, label):
    tx = build_coinbase(psz, pubhex, reward)
    merkle_internal = dsha(tx)                     # single tx: merkle = txid (internal order)
    target = compact_target(bits)
    nonce = 0
    while True:
        hdr = struct.pack("<i", 1) + b"\x00" * 32 + merkle_internal + struct.pack("<III", ntime, bits, nonce)
        h = dsha(hdr)
        if int.from_bytes(h, "little") <= target: break
        nonce += 1
    disp = lambda b: b[::-1].hex()
    r = {"label": label, "pszTimestamp": psz, "nTime": ntime, "nBits": hex(bits),
         "nNonce": nonce, "pubkey": pubhex, "reward_sats": reward,
         "coinbase_txid(=merkle root)": disp(merkle_internal),
         "genesis_hash": disp(h), "target": format(target, "064x"),
         "tries": nonce + 1}
    print(json.dumps(r, indent=2)); return r

if __name__ == "__main__":
    pub = open("/tmp/tn_genesis_pub.hex").read().strip()
    # MAIN: time = 2026-10-23 00:00:00 UTC
    import datetime
    nt = int(datetime.datetime(2026, 10, 23, tzinfo=datetime.timezone.utc).timestamp())
    grind("Treeneesu 23/Oct/2026 - a learning chain with no monetary value",
          pub, nt, 0x1e0fffff, 50 * 100_000_000, "treeneesu-main")
