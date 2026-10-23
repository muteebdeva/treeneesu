#!/usr/bin/env python3
"""Independent model of Bitcoin Core's CalculateNextWorkRequired (pow.cpp),
used to recompute pow_tests expectations for Treeneesu parameters.
Control: with Bitcoin's powLimit it must reproduce the four expected values
currently hardcoded in pow_tests.cpp (which were computed for Bitcoin)."""

def set_compact(bits):
    size = bits >> 24
    word = bits & 0x007fffff
    if size <= 3:
        return word >> (8 * (3 - size))
    return word << (8 * (size - 3))

def get_compact(n):
    size = (n.bit_length() + 7) // 8
    if size <= 3:
        word = n << (8 * (3 - size))
    else:
        word = n >> (8 * (size - 3))
    if word & 0x00800000:
        word >>= 8
        size += 1
    return (size << 24) | (word & 0x007fffff)

def calc_next_work(last_bits, last_time, first_time, pow_limit, timespan=1209600):
    actual = last_time - first_time
    actual = max(actual, timespan // 4)
    actual = min(actual, timespan * 4)
    new = (set_compact(last_bits) * actual) // timespan
    if new > pow_limit:
        new = pow_limit
    return get_compact(new)

BTC_LIMIT = set_compact(0x1d00ffff)
TNSU_LIMIT = set_compact(0x1e01ffff)

cases = [
    # (name, last_bits, last_time, first_time, bitcoin_expected)
    ("get_next_work",            0x1d00ffff, 1262152739, 1261130161, 0x1d00d86a),
    ("get_next_work_pow_limit",  0x1d00ffff, 1233061996, 1231006505, 0x1d00ffff),
    ("lower_limit_actual",       0x1c05a3f4, 1279297671, 1279008237, 0x1c0168fd),
    ("upper_limit_actual",       0x1c387f6f, 1269211443, 1263163443, 0x1d00e1fd),
]
print("== CONTROL (Bitcoin powLimit) ==")
for name, bits, lt, ft, exp in cases:
    got = calc_next_work(bits, lt, ft, BTC_LIMIT)
    print(f"{name}: model={got:#010x} expected={exp:#010x} {'OK' if got == exp else 'MISMATCH'}")
    assert got == exp
print("control passed\n== TREENEESU powLimit ==")
for name, bits, lt, ft, exp in cases:
    got = calc_next_work(bits, lt, ft, TNSU_LIMIT)
    print(f"{name}: model={got:#010x} (bitcoin expected was {exp:#010x})")
# case 2 redesigned: start at Treeneesu powLimit so the cap engages
got2 = calc_next_work(0x1e01ffff, 1233061996, 1231006505, TNSU_LIMIT)
print(f"pow_limit case redesigned (start at limit): model={got2:#010x} -> expect 0x1e01ffff")
assert got2 == 0x1e01ffff
print("pow_limit redesign OK")
