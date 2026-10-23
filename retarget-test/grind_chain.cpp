// Treeneesu retarget-test chain grinder.
// Builds coinbase-only blocks for heights 1..N on the REAL Treeneesu main
// parameters (bits schedule passed in), grinding each header's nonce with
// Bitcoin Core's own CSHA256 (linked from the build-final objects, SHA-NI
// included). Output: one "<height> <blockhex>" line per block.
#include <crypto/sha256.h>
#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <thread>
#include <vector>
#include <algorithm>

static void dsha(const uint8_t* in, size_t len, uint8_t out[32]) {
    uint8_t tmp[32];
    CSHA256().Write(in, len).Finalize(tmp);
    CSHA256().Write(tmp, 32).Finalize(out);
}
static void put32(std::vector<uint8_t>& v, uint32_t x) { for (int i = 0; i < 4; i++) v.push_back((x >> (8 * i)) & 0xff); }
static void put64(std::vector<uint8_t>& v, uint64_t x) { for (int i = 0; i < 8; i++) v.push_back((x >> (8 * i)) & 0xff); }
static std::string hex(const uint8_t* p, size_t n) { static const char* H = "0123456789abcdef"; std::string s; s.reserve(2 * n); for (size_t i = 0; i < n; i++) { s += H[p[i] >> 4]; s += H[p[i] & 15]; } return s; }
static std::string hex(const std::vector<uint8_t>& v) { return hex(v.data(), v.size()); }

// compact target -> 32-byte big-endian-ish comparison value (as uint256 LE bytes target integer)
static void target_of(uint32_t bits, uint8_t tgt_le[32]) {
    memset(tgt_le, 0, 32);
    uint32_t exp = bits >> 24, mant = bits & 0x007fffff;
    // value = mant * 256^(exp-3); store little-endian
    uint64_t m = mant;
    int shift_bytes = (int)exp - 3;
    // write mant (<=3 bytes) at byte offset shift_bytes, little-endian value
    for (int i = 0; i < 3; i++) {
        int pos = shift_bytes + i;
        if (pos >= 0 && pos < 32) tgt_le[pos] = (m >> (8 * i)) & 0xff;
    }
    (void)shift_bytes;
}
static bool hash_le_target(const uint8_t h[32], const uint8_t tgt[32]) {
    // both little-endian byte arrays representing 256-bit integers (hash internal order)
    for (int i = 31; i >= 0; i--) { if (h[i] != tgt[i]) return h[i] < tgt[i]; }
    return true;
}

int main(int argc, char** argv) {
    // args: genesis_hash_display_hex T0 spacing B1 B2 retarget_height last_height outfile subsidy_sats
    const char* gen_hex = argv[1];
    uint32_t T0 = strtoul(argv[2], nullptr, 10);
    uint32_t spacing = strtoul(argv[3], nullptr, 10);
    uint32_t B1 = strtoul(argv[4], nullptr, 0), B2 = strtoul(argv[5], nullptr, 0);
    int32_t rhe = atoi(argv[6]);
    int32_t last = atoi(argv[7]);
    const char* outpath = argv[8];
    uint64_t subsidy = strtoull(argv[9], nullptr, 10);

    SHA256AutoDetect();
    uint8_t prev[32]; // internal (little-endian) order
    for (int i = 0; i < 32; i++) { unsigned int b; sscanf(gen_hex + 62 - 2 * i, "%2x", &b); prev[i] = (uint8_t)b; }

    // Resume support: if the output file already has blocks, continue the
    // chain from its last line (construction is deterministic per height).
    int32_t start_h = 1;
    {
        FILE* existing = fopen(outpath, "r");
        if (existing) {
            char line[65536]; std::string lastline;
            while (fgets(line, sizeof(line), existing)) { if (line[0] >= '0' && line[0] <= '9') lastline = line; }
            fclose(existing);
            if (!lastline.empty()) {
                int lh; char hashdisp[65];
                if (sscanf(lastline.c_str(), "%d %*s %64s", &lh, hashdisp) == 2 && lh >= 1) {
                    for (int i = 0; i < 32; i++) { unsigned int b; sscanf(hashdisp + 62 - 2 * i, "%2x", &b); prev[i] = (uint8_t)b; }
                    start_h = lh + 1;
                    fprintf(stderr, "resuming at height %d\n", start_h);
                }
            }
        }
    }
    FILE* out = fopen(outpath, "a");
    uint8_t tgt1[32], tgt2[32]; target_of(B1, tgt1); target_of(B2, tgt2);

    for (int32_t h = start_h; h <= last; h++) {
        uint32_t bits = (h < rhe) ? B1 : B2;
        const uint8_t* tgt = (h < rhe) ? tgt1 : tgt2;
        uint32_t ntime = T0 + spacing * (uint32_t)h;
        // coinbase tx: version 1, 1 in, 1 out
        std::vector<uint8_t> tx;
        put32(tx, 1); tx.push_back(1);
        for (int i = 0; i < 32; i++) tx.push_back(0);
        put32(tx, 0xffffffff);
        // scriptSig: BIP34 height (CScriptNum minimal) + marker byte
        std::vector<uint8_t> ss;
        { uint32_t x = h; std::vector<uint8_t> num; while (x) { num.push_back(x & 0xff); x >>= 8; } if (!num.empty() && (num.back() & 0x80)) num.push_back(0); ss.push_back((uint8_t)num.size()); ss.insert(ss.end(), num.begin(), num.end()); ss.push_back(0x2a); }
        tx.push_back((uint8_t)ss.size()); tx.insert(tx.end(), ss.begin(), ss.end());
        put32(tx, 0xffffffff);
        tx.push_back(1); put64(tx, subsidy);
        tx.push_back(1); tx.push_back(0x51); // OP_TRUE output
        put32(tx, 0);
        uint8_t merkle[32]; dsha(tx.data(), tx.size(), merkle);
        // block = header + varint(1) + tx
        std::vector<uint8_t> blk;
        put32(blk, 0x20000000);
        blk.insert(blk.end(), prev, prev + 32);
        blk.insert(blk.end(), merkle, merkle + 32);
        put32(blk, ntime); put32(blk, bits);
        size_t nonce_off = blk.size(); put32(blk, 0);
        blk.push_back(1); blk.insert(blk.end(), tx.begin(), tx.end());
        // grind (2 threads, nonce stride 2)
        std::atomic<uint32_t> found{0}; std::atomic<bool> done{false};
        auto work = [&](uint32_t start) {
            std::vector<uint8_t> b = blk; uint8_t hh[32];
            for (uint32_t n = start; !done.load(std::memory_order_relaxed); n += 2) {
                memcpy(b.data() + nonce_off, &n, 4); // little-endian host
                dsha(b.data(), 80, hh);
                if (hash_le_target(hh, tgt)) { found.store(n); done.store(true); return; }
            }
        };
        std::thread t0(work, 0), t1(work, 1); t0.join(); t1.join();
        uint32_t n = found.load(); memcpy(blk.data() + nonce_off, &n, 4);
        uint8_t bh[32]; dsha(blk.data(), 80, bh);
        std::vector<uint8_t> disp(bh, bh + 32); std::reverse(disp.begin(), disp.end());
        fprintf(out, "%d %s %s\n", h, hex(blk).c_str(), hex(disp).c_str());
        fflush(out);
        memcpy(prev, bh, 32);
        if (h % 500 == 0) fprintf(stderr, "height %d ground (nonce %u)\n", h, n);
    }
    fclose(out);
    return 0;
}
