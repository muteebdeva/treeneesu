#!/usr/bin/env python3
"""Independent Python implementation of BIP324 (v2 transport) packet encoding.

Written from the BIP324 algorithm structure; EllSwift decode transcribed from
the algorithm description in libsecp256k1's ellswift module (constants c1/c2).
Validation strategy: this implementation must reproduce, byte-for-byte, every
field of the existing Bitcoin-mainnet test vectors in bip324_tests.cpp
(control run) before its Treeneesu-magic outputs are trusted.
"""
import hashlib, hmac as hmac_mod, struct

# ---------------- secp256k1 ----------------
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

def pt_add(a, b):
    if a is None: return b
    if b is None: return a
    x1, y1 = a; x2, y2 = b
    if x1 == x2 and (y1 + y2) % P == 0: return None
    if a == b:
        lam = (3 * x1 * x1) * pow(2 * y1, -1, P) % P
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    return (x3, (lam * (x1 - x3) - y1) % P)

def pt_mul(k, pt=G):
    k %= N
    r = None
    while k:
        if k & 1: r = pt_add(r, pt)
        pt = pt_add(pt, pt)
        k >>= 1
    return r

def on_curve_x_frac(n, d):
    # x = n/d is a valid x iff (n^3 + 7 d^3) * d is a quadratic residue (or zero)
    v = (pow(n, 3, P) + 7 * pow(d, 3, P)) * d % P
    return v == 0 or pow(v, (P - 1) // 2, P) == 1

C1 = 0x851695d49a83f8ef919bb86153cbcb16630fb68aed0a766a3ec693d68e6afa40
C2 = 0x7ae96a2b657c07106e64479eac3434e99cf0497512f58995c1396c28719501ee

def ellswift_decode_x(enc64):
    u = int.from_bytes(enc64[:32], 'big') % P
    t = int.from_bytes(enc64[32:], 'big') % P
    u1 = 1 if u == 0 else u
    s = 1 if t == 0 else (t * t) % P
    g = (pow(u1, 3, P) + 7) % P
    if (g + s) % P == 0:
        s = 4 * s % P
    p = (g + s) % P
    # candidate x3 = (3*s*u^3 - (g+s)^2) / (3*s*u^2)
    d3 = 3 * s * u1 * u1 % P
    n3 = (3 * s * pow(u1, 3, P) - p * p) % P
    if on_curve_x_frac(n3, d3):
        return n3 * pow(d3, -1, P) % P
    # candidate x2 = u*(c1*s + c2*g) / (g+s)
    n2 = u1 * (C1 * s + C2 * g) % P
    if on_curve_x_frac(n2, p):
        return n2 * pow(p, -1, P) % P
    # x1 = -(x2 + u)
    x2 = n2 * pow(p, -1, P) % P
    return (-(x2 + u1)) % P

def tagged_hash(tag, msg):
    taghash = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(taghash + taghash + msg).digest()

def bip324_ecdh(priv_bytes, ellswift_ours, ellswift_theirs, initiating):
    x = ellswift_decode_x(ellswift_theirs)
    y = pow((pow(x, 3, P) + 7) % P, (P + 1) // 4, P)
    shared = pt_mul(int.from_bytes(priv_bytes, 'big'), (x, y))
    sx = shared[0].to_bytes(32, 'big')
    ell_a = ellswift_ours if initiating else ellswift_theirs
    ell_b = ellswift_theirs if initiating else ellswift_ours
    return tagged_hash("bip324_ellswift_xonly_ecdh", ell_a + ell_b + sx)

# ---------------- HKDF (Core's CHKDF_HMAC_SHA256_L32) ----------------
class HKDF:
    def __init__(self, ikm, salt):
        self.prk = hmac_mod.new(salt, ikm, hashlib.sha256).digest()
    def expand32(self, info):
        return hmac_mod.new(self.prk, info.encode() + b"\x01", hashlib.sha256).digest()

# ---------------- ChaCha20 ----------------
def rotl32(v, c): return ((v << c) | (v >> (32 - c))) & 0xFFFFFFFF

def chacha_block(key, counter, nonce12):
    consts = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]
    state = consts + list(struct.unpack('<8I', key)) + [counter] + list(struct.unpack('<3I', nonce12))
    x = state[:]
    def qr(a, b, c, d):
        x[a] = (x[a] + x[b]) & 0xFFFFFFFF; x[d] ^= x[a]; x[d] = rotl32(x[d], 16)
        x[c] = (x[c] + x[d]) & 0xFFFFFFFF; x[b] ^= x[c]; x[b] = rotl32(x[b], 12)
        x[a] = (x[a] + x[b]) & 0xFFFFFFFF; x[d] ^= x[a]; x[d] = rotl32(x[d], 8)
        x[c] = (x[c] + x[d]) & 0xFFFFFFFF; x[b] ^= x[c]; x[b] = rotl32(x[b], 7)
    for _ in range(10):
        qr(0, 4, 8, 12); qr(1, 5, 9, 13); qr(2, 6, 10, 14); qr(3, 7, 11, 15)
        qr(0, 5, 10, 15); qr(1, 6, 11, 12); qr(2, 7, 8, 13); qr(3, 4, 9, 14)
    out = [(a + b) & 0xFFFFFFFF for a, b in zip(x, state)]
    return struct.pack('<16I', *out)

def chacha20_xor(key, counter, nonce12, data):
    out = bytearray()
    ctr = counter
    for off in range(0, len(data), 64):
        ks = chacha_block(key, ctr, nonce12)
        chunk = data[off:off + 64]
        out.extend(a ^ b for a, b in zip(chunk, ks))
        ctr += 1
    return bytes(out)

# ---------------- Poly1305 ----------------
def poly1305_mac(msg, key):
    r = int.from_bytes(key[:16], 'little') & 0x0ffffffc0ffffffc0ffffffc0fffffff
    s = int.from_bytes(key[16:], 'little')
    acc = 0
    pp = (1 << 130) - 5
    for i in range(0, len(msg), 16):
        chunk = msg[i:i + 16]
        n = int.from_bytes(chunk, 'little') + (1 << (8 * len(chunk)))
        acc = ((acc + n) * r) % pp
    return ((acc + s) % (1 << 128)).to_bytes(16, 'little')

def pad16(b): return b"\x00" * ((16 - len(b) % 16) % 16)

def aead_encrypt(key, nonce12, plaintext, aad):
    poly_key = chacha_block(key, 0, nonce12)[:32]
    ciphertext = chacha20_xor(key, 1, nonce12, plaintext)
    mac_data = aad + pad16(aad) + ciphertext + pad16(ciphertext) + struct.pack('<Q', len(aad)) + struct.pack('<Q', len(ciphertext))
    return ciphertext + poly1305_mac(mac_data, poly_key)

# ---------------- FSChaCha20 (length cipher) ----------------
class FSChaCha20:
    def __init__(self, key, rekey_interval=224):
        self.key = key
        self.rekey_interval = rekey_interval
        self.chunk_counter = 0
        self.rekey_counter = 0
        self.stream = b""
        self.pos = 0
    def _fill(self, n):
        while len(self.stream) - self.pos < n:
            nonce = struct.pack('<I', 0) + struct.pack('<Q', self.rekey_counter)
            block_idx = (self.pos + (len(self.stream) - self.pos)) // 64
            # generate stream contiguously from position 0 of current epoch
            # simpler: regenerate whole stream up to needed length
            total = self.pos + n
            ks = bytearray()
            ctr = 0
            while len(ks) < total:
                ks.extend(chacha_block(self.key, ctr, nonce))
                ctr += 1
            self.stream = bytes(ks)
    def crypt(self, data):
        self._fill(len(data))
        out = bytes(a ^ b for a, b in zip(data, self.stream[self.pos:self.pos + len(data)]))
        self.pos += len(data)
        self.chunk_counter += 1
        if self.chunk_counter == self.rekey_interval:
            self._fill(32)
            new_key = self.stream[self.pos:self.pos + 32]
            self.pos += 32
            self.key = new_key
            self.rekey_counter += 1
            self.chunk_counter = 0
            self.stream = b""
            self.pos = 0
        return out

# ---------------- FSChaCha20Poly1305 (payload cipher) ----------------
class FSChaCha20Poly1305:
    def __init__(self, key, rekey_interval=224):
        self.key = key
        self.rekey_interval = rekey_interval
        self.packet_counter = 0
        self.rekey_counter = 0
    def encrypt(self, header_plus_contents, aad):
        nonce = struct.pack('<I', self.packet_counter) + struct.pack('<Q', self.rekey_counter)
        out = aead_encrypt(self.key, nonce, header_plus_contents, aad)
        self.packet_counter += 1
        if self.packet_counter == self.rekey_interval:
            nonce_ks = struct.pack('<I', 0xFFFFFFFF) + struct.pack('<Q', self.rekey_counter)
            ks_block = chacha_block(self.key, 1, nonce_ks)  # AEAD Keystream skips block 0 (poly key block)
            self.key = ks_block[:32]
            self.packet_counter = 0
            self.rekey_counter += 1
        return out

# ---------------- BIP324Cipher ----------------
class BIP324Cipher:
    def __init__(self, priv_bytes, ellswift_ours, magic):
        self.priv = priv_bytes
        self.ellswift_ours = ellswift_ours
        self.magic = magic
    def initialize(self, ellswift_theirs, initiating):
        ecdh = bip324_ecdh(self.priv, self.ellswift_ours, ellswift_theirs, initiating)
        salt = b"bitcoin_v2_shared_secret" + self.magic
        hkdf = HKDF(ecdh, salt)
        i_l = hkdf.expand32("initiator_L"); i_p = hkdf.expand32("initiator_P")
        r_l = hkdf.expand32("responder_L"); r_p = hkdf.expand32("responder_P")
        if initiating:
            self.send_l, self.send_p = FSChaCha20(i_l), FSChaCha20Poly1305(i_p)
            self.recv_l, self.recv_p = FSChaCha20(r_l), FSChaCha20Poly1305(r_p)
        else:
            self.send_l, self.send_p = FSChaCha20(r_l), FSChaCha20Poly1305(r_p)
            self.recv_l, self.recv_p = FSChaCha20(i_l), FSChaCha20Poly1305(i_p)
        gt = hkdf.expand32("garbage_terminators")
        if initiating:
            self.send_gt, self.recv_gt = gt[:16], gt[16:]
        else:
            self.recv_gt, self.send_gt = gt[:16], gt[16:]
        self.session_id = hkdf.expand32("session_id")
    def encrypt(self, contents, aad, ignore):
        length = len(contents)
        len_bytes = bytes([length & 0xFF, (length >> 8) & 0xFF, (length >> 16) & 0xFF])
        enc_len = self.send_l.crypt(len_bytes)
        header = bytes([0x80 if ignore else 0x00])
        enc_payload = self.send_p.encrypt(header + contents, aad)
        return enc_len + enc_payload
