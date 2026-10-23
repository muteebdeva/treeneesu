// Copyright (c) 2013-present The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <boost/test/unit_test.hpp>

#include <clientversion.h>
#include <key.h>
#include <key_io.h>
#include <streams.h>
#include <test/util/setup_common.h>
#include <util/bip32.h>
#include <util/strencodings.h>

#include <string>
#include <vector>

namespace {

struct TestDerivation {
    std::string pub;
    std::string prv;
    unsigned int nChild;
};

struct TestVector {
    std::string strHexMaster;
    std::vector<TestDerivation> vDerive;

    explicit TestVector(std::string strHexMasterIn) : strHexMaster(strHexMasterIn) {}

    TestVector& operator()(std::string pub, std::string prv, unsigned int nChild) {
        vDerive.emplace_back();
        TestDerivation &der = vDerive.back();
        der.pub = pub;
        der.prv = prv;
        der.nChild = nChild;
        return *this;
    }
};

TestVector test1 =
  TestVector("000102030405060708090a0b0c0d0e0f")
    ("ds3aHFeAyau6iYyunRiNZCFUgS8UfrBxfqzaMKMDHAtdSgrFDomkNrAUs3myBMo4pdzBnLcS35V75Z9NMm9i6Hm8efQGdqEJYjUJCkBNbdKwsKH",
     "ds3Z8p2h4LrJEXxvQa5nGDCnNGRSXtkQctG8gfwmQ7q8ZCiwYJNmi27moVNtaPy1EtBLtp9SYjQ173aZL4wRXYNgBRWm6UYT5AJH1chxnkFiFA9",
     BIP32_HARDENED_FLAG)
    ("ds3aHHuayJCZop6tw2r5kx87ZUEazfkK3vUb2vn7FGGkQt3Xb64vo5hZzC8NxdMmZwtinYtzuK2XpCDTLA7r3KVWiYrzqU2ZU3NWigJvuE6rCLu",
     "ds3Z8rJ7449mKo5uZBDVTy5RFJXYriJkzxk9NHNfNDDFXPvDuafx8FervdjJMfKLebZJbs38v2isVQRS3py9B8eryVbHAMDbK81AidLpDsPdYZJ",
     1)
    ("ds3aHL5iB5kTCWyxmUtXVD1zAD8F43jR3xCsyFSwqY3ZMWqjpda4Wt7swm2cNhpLytc4kGX3gjUdvnhvvTrfWefQQCgw8fsQwgNnMQqiCDQokCy",
     "ds3Z8tUEFqheiVxyPdFwCDyHr3RCv6HrzzUSJc3VxUz4U2iS98B5r45AtCdXmiWQFXLM3wnpirKJa7NrBmVNJUSqkf5ig8BKNsn2PRfBkqbXyyr",
     BIP32_HARDENED_FLAG | 2)
    ("ds3aHNgzDcaJuPqNdegcjoRMXDAPHCbwKVnsJngd5sLiXPDBEUmBKdxJrCaXvj1BRm3P6ncnJ7TFJjGuNnzxDkCwTeqmiZqZ2dSU56krHSajDxr",
     "ds3Z8w5WJNXWRNpPFo42SpNfD3TM9FAPGY4Re9HBCpHDdu5sYyNCeoubneBTKkj2DkqqZQpDKKGDzXCkQyE7tVN2skXP2jjsXp1xzhQQPR9mJER",
     2)
    ("ds3aHQvP43hG5sWMi8ALS4dSQiKhN1tfx674kGZvLpsBqpmnbaPYPQeg3n3Tc3zZqZC7a6jxS7wCMUB1wDLxK3e9BFK2dMPjrpLJ5nfhRzZXsK1",
     "ds3Z8yJu8oeTbrVNLGXk95ak6YcfE4T7u8Nd5dAUTmogxLeUv4zZiabxzDeP158UgRFGdCwuwEVnuLeutA8a5uuP597RRypy5tqg9fsZtuDhesg",
     1000000000)
    ("ds3aHSe9XjJWCztZETwnYcCAiRKhAFTymav6YWxUb7FL3uAHJhnvupuLJtCXEsuWgpGq3o2VwTrztfscXdjyQu8z2WU9VtopfHuvtkHcg9PdcoC",
     "ds3Z912fcVFhiysZrcKCFd9UQFcf2J2RidBessZ2i4BqAR2ydCPxEzrdFKoSdvugbLNMEcMAibUjkPC2tL8wcyv7C6kxmUbCCobPS1Rve5kMBfk",
     0);

TestVector test2 =
  TestVector("fffcf9f6f3f0edeae7e4e1dedbd8d5d2cfccc9c6c3c0bdbab7b4b1aeaba8a5a29f9c999693908d8a8784817e7b7875726f6c696663605d5a5754514e4b484542")
    ("ds3aHFeAyau6iYyun3DhfMKm8drEv3LPMUFQ2u8wa7dTR4y7WnnwYzwRHwwZXTt3XtM9gtrDwk9GUded5YswDUgHnaQDVmRmPDxxX7rUsUa9ee9",
     "ds3Z8p2h4LrJEXxvQBb7NNH4pU9Cn5tqJWWxNFjVh4ZxXaqoqHPxtAtiEPYUvTk4RPjS8rtsJ1rTP9ckRbfXZxmNnnqXYtchDWD1asLC9mPdNHe",
     0)
    ("ds3aHJuvFJb4CZozJJozo8heCSFmH15e4Sjgb4tJjveuVUq5CmEv8GHVSnWp6vqwKyMauDLPoy91siVbEiJd6dNi8B4VmpASHa7Leby9Jm4XWHE",
     "ds3Z8sJSL4YFiYnzvTBQW9ewtGYj93e61V1EvRUrrsbQbzhmXFqwTSEnPE7jVy1s4TaGYX8hC2GBpK2sn7JM8FGRj1zvZ52kbzNkiHEkX2MKZTF",
     0xFFFFFFFF)
    ("ds3aHL4yVucaaTz6UB2BDahHfmwKfkJYbvuNgDxqfKZg9DbTf4UNk9hoerJQiK645hxggjFwTozdAvvBuPAxsXrprKX8JtnVeJNMWzEk9YBrgaV",
     "ds3Z8tTVafZn6Sy76KPavbebMcEHXnrzYyAw1aZPnGWBFjU9yZ5Q5Kf6bHuL7KVqniJkSkTay3TpsKXzDM37rcsZJKSUyoG6NW71W4aHHT8neFv",
     1)
    ("ds3aHNswuvbWk7HHZnhKHEqrdisZ1HB3i7pdzfThWPE1T6wuKtLY3fEWYkgnZ7HBsaeyGuiVJT5rp4E1zBRynSHn7ez2uAzLrqoZSkuhPzmjGA5",
     "ds3Z8wGTzgYiG6GJBw4izFoAKZAWsKjVfA6CL24FdLAWZcpbeNwZNqBoVCHhx7hTpRWSkhpHiLYDGsDCY3pGuWPwJoFn7ZnuDc5Pys11m5RkjUn",
     0xFFFFFFFE)
    ("ds3aHQ3yptXsMWEzrjvv1ifQ1EZjv1eQm6T92NBb36vRHsD9nEfU9LAX5H3tBmQh4xBREMN86x9ZrfYsdpbNUKQHq1gVB5JqR8tyJyzGvuqEzNx",
     "ds3Z8xSVueV4sVE1UtJKijchh4rhn4Cri8ihMin9A3rvQP5r6jGVUW7p1ieoapRrSqtjJH6z2AKCfEnnMAueRTJRzdvwwWLDMp72KT1Xpus4D7S",
     2)
    ("ds3aHRR1nKkNsgZEc17ojno5yywiK5BX1RNDgXoUStGuvf4jrS13Jy6HFqztGAUyCXY7kQaMNseykNZs8FesJR6C9GY4pF8vMWBhzHBTbZkpYy7",
     "ds3Z8yoXs5haPfYFE9VDSokPfpEgB7jxxTdn1tQ2ZqDR3AwSAvc4e93aCHbofE6rbryoLaxiJux27LdUPioA9mff3cffkMqiREEk1pM5uTvDSJz",
     0);

TestVector test3 =
  TestVector("4b381541583be4423346c643850da4b320e46a87ae3d2a4e6da11eba819cd4acba45d239319ac14f863b8d5ab5a0d0c64d2e8a1e7d1457df2e5a3c51c73235be")
    ("ds3aHFeAyau6iYyum6fsBjpZLd7GngfV7LQfkEuVyQf1gm3uV32DD9BPFDB61TR2MUvnryc5mk2GsJUUWrWr4BijCv4Md1Kz7nQoJqNBQ2yArnN",
     "ds3Z8p2h4LrJEXxvPF3Gtkms2TQEejDw4NgE5bW46MbWoGvboXdEYK8gBen1QTUENQxmDZZcrwYZHaMTnFGqoPuoaGLn5BBLQwYysazYobCLsMr",
      BIP32_HARDENED_FLAG)
    ("ds3aHJ1NiYjEPvMFxdmGQtA4PsrwV3GsGBpa9j9SneLrd4yGk49fndxFKfxoKBFY5qXY4M6vYhn1iFfy9KTBzReunALJJ7Gsfdubo1j64Qc7kfW",
     "ds3Z8rPtoJgRuuLGan8g7u7N5i9uM5qKDE68V5jzubHMjaqy4Ykh7ouYG7ZiiDpaiNHgfiD2stLRwJyvRnuzNcVZL2YQWK6PA6pnzbxCm2vDH91",
      0);

TestVector test4 =
  TestVector("3ddd5602285899a946114506157c7997e5444528f3003f6134712147db19b678")
    ("ds3aHFeAyau6iYyuoABS2UBN9NaAQvFf2apQzNbuM9LbZHtbKvqYR3n9TRjBhafhNvWrSWjdvRFTp5FDKjHyUPjeHmvGPRd4g6NcDS3QUqyuvSx",
     "ds3Z8p2h4LrJEXxvRJYqjV8fqCs8Gxp6yd5yKjCTU6H6fomHeRSZkDjSPsL76ckMP9Mwo2XEy8RhDuZERFu8TVAif61AaR3NTpSe9irhZmDs6o9",
     BIP32_HARDENED_FLAG)
    ("ds3aHJoHMy1m6K6MS3CZeo799mfvrr8vjtLxjgDZh7WaCjxZpTteyPCsbUQXsAwTQYsyrcVzsTe5R1BTrez3BBC3P5yJRk42YuTzGEbTHFdiXjR",
     "ds3Z8sBoSixxcJ5N4BZyMp4SqbxtithNgvcX52p7p4T5KFqG8xVgJZAAXv1TGAfbRxYJm1YgVhbvYMfKMv6E4rqMfit6RoM3fjte8ytWJgUkCK4",
     BIP32_HARDENED_FLAG | 1)
    ("ds3aHLvy1xQmc38x7C4Co523FeFn2nK1Ep3mPcGPTs2mrw41bZDAqsgapbNQm7hzFjWfSQ7MmEaBsTXSq9Jwdn1C6NufmXu5Wdww8exMLq94LSF",
     "ds3Z8uKV6iMy827xjLRcW5yLwUYjtpsTBrKKixrwaoyGySvhv3pCB3dsm2yLA8dgVMa8qmwngJRtJzmC4suwTnnUx7MKg944mn8xzfSCQHTswJ7",
     0);

const std::vector<std::string> TEST5 = {
    "xpub661MyMwAqRbcEYS8w7XLSVeEsBXy79zSzH1J8vCdxAZningWLdN3zgtU6LBpB85b3D2yc8sfvZU521AAwdZafEz7mnzBBsz4wKY5fTtTQBm",
    "xprv9s21ZrQH143K24Mfq5zL5MhWK9hUhhGbd45hLXo2Pq2oqzMMo63oStZzFGTQQD3dC4H2D5GBj7vWvSQaaBv5cxi9gafk7NF3pnBju6dwKvH",
    "xpub661MyMwAqRbcEYS8w7XLSVeEsBXy79zSzH1J8vCdxAZningWLdN3zgtU6Txnt3siSujt9RCVYsx4qHZGc62TG4McvMGcAUjeuwZdduYEvFn",
    "xprv9s21ZrQH143K24Mfq5zL5MhWK9hUhhGbd45hLXo2Pq2oqzMMo63oStZzFGpWnsj83BHtEy5Zt8CcDr1UiRXuWCmTQLxEK9vbz5gPstX92JQ",
    "xpub661MyMwAqRbcEYS8w7XLSVeEsBXy79zSzH1J8vCdxAZningWLdN3zgtU6N8ZMMXctdiCjxTNq964yKkwrkBJJwpzZS4HS2fxvyYUA4q2Xe4",
    "xprv9s21ZrQH143K24Mfq5zL5MhWK9hUhhGbd45hLXo2Pq2oqzMMo63oStZzFAzHGBP2UuGCqWLTAPLcMtD9y5gkZ6Eq3Rjuahrv17fEQ3Qen6J",
    "xprv9s2SPatNQ9Vc6GTbVMFPFo7jsaZySyzk7L8n2uqKXJen3KUmvQNTuLh3fhZMBoG3G4ZW1N2kZuHEPY53qmbZzCHshoQnNf4GvELZfqTUrcv",
    "xpub661no6RGEX3uJkY4bNnPcw4URcQTrSibUZ4NqJEw5eBkv7ovTwgiT91XX27VbEXGENhYRCf7hyEbWrR3FewATdCEebj6znwMfQkhRYHRLpJ",
    "xprv9s21ZrQH4r4TsiLvyLXqM9P7k1K3EYhA1kkD6xuquB5i39AU8KF42acDyL3qsDbU9NmZn6MsGSUYZEsuoePmjzsB3eFKSUEh3Gu1N3cqVUN",
    "xpub661MyMwAuDcm6CRQ5N4qiHKrJ39Xe1R1NyfouMKTTWcguwVcfrZJaNvhpebzGerh7gucBvzEQWRugZDuDXjNDRmXzSZe4c7mnTK97pTvGS8",
    "DMwo58pR1QLEFihHiXPVykYB6fJmsTeHvyTp7hRThAtCX8CvYzgPcn8XnmdfHGMQzT7ayAmfo4z3gY5KfbrZWZ6St24UVf2Qgo6oujFktLHdHY4",
    "DMwo58pR1QLEFihHiXPVykYB6fJmsTeHvyTp7hRThAtCX8CvYzgPcn8XnmdfHPmHJiEDXkTiJTVV9rHEBUem2mwVbbNfvT2MTcAqj3nesx8uBf9",
    "xprv9s21ZrQH143K24Mfq5zL5MhWK9hUhhGbd45hLXo2Pq2oqzMMo63oStZzF93Y5wvzdUayhgkkFoicQZcP3y52uPPxFnfoLZB21Teqt1VvEHx",
    "xprv9s21ZrQH143K24Mfq5zL5MhWK9hUhhGbd45hLXo2Pq2oqzMMo63oStZzFAzHGBP2UuGCqWLTAPLcMtD5SDKr24z3aiUvKr9bJpdrcLg1y3G",
    "xpub661MyMwAqRbcEYS8w7XLSVeEsBXy79zSzH1J8vCdxAZningWLdN3zgtU6Q5JXayek4PRsn35jii4veMimro1xefsM58PgBMrvdYre8QyULY",
    "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHL"
};

void RunTest(const TestVector& test)
{
    std::vector<std::byte> seed{ParseHex<std::byte>(test.strHexMaster)};
    CExtKey key;
    CExtPubKey pubkey;
    key.SetSeed(seed);
    pubkey = key.Neuter();
    for (const TestDerivation &derive : test.vDerive) {
        unsigned char data[74];
        key.Encode(data);
        pubkey.Encode(data);

        // Test private key
        BOOST_CHECK(EncodeExtKey(key) == derive.prv);
        BOOST_CHECK(DecodeExtKey(derive.prv) == key); //ensure a base58 decoded key also matches

        // Test public key
        BOOST_CHECK(EncodeExtPubKey(pubkey) == derive.pub);
        BOOST_CHECK(DecodeExtPubKey(derive.pub) == pubkey); //ensure a base58 decoded pubkey also matches

        // Derive new keys
        CExtKey keyNew;
        BOOST_CHECK(key.Derive(keyNew, derive.nChild));
        CExtPubKey pubkeyNew = keyNew.Neuter();
        if (!(derive.nChild & BIP32_HARDENED_FLAG)) {
            // Compare with public derivation
            CExtPubKey pubkeyNew2;
            BOOST_CHECK(pubkey.Derive(pubkeyNew2, derive.nChild));
            BOOST_CHECK(pubkeyNew == pubkeyNew2);
        }
        key = keyNew;
        pubkey = pubkeyNew;
    }
}

}  // namespace

BOOST_FIXTURE_TEST_SUITE(bip32_tests, BasicTestingSetup)

BOOST_AUTO_TEST_CASE(bip32_test1) {
    RunTest(test1);
}

BOOST_AUTO_TEST_CASE(bip32_test2) {
    RunTest(test2);
}

BOOST_AUTO_TEST_CASE(bip32_test3) {
    RunTest(test3);
}

BOOST_AUTO_TEST_CASE(bip32_test4) {
    RunTest(test4);
}

BOOST_AUTO_TEST_CASE(bip32_test5) {
    for (const auto& str : TEST5) {
        auto dec_extkey = DecodeExtKey(str);
        auto dec_extpubkey = DecodeExtPubKey(str);
        BOOST_CHECK_MESSAGE(!dec_extkey.key.IsValid(), "Decoding '" + str + "' as xprv should fail");
        BOOST_CHECK_MESSAGE(!dec_extpubkey.pubkey.IsValid(), "Decoding '" + str + "' as xpub should fail");
    }
}

BOOST_AUTO_TEST_CASE(bip32_derive_ext_key)
{
    const CExtKey master{DecodeExtKey(test1.vDerive[0].prv)};
    const std::vector<uint32_t> path{test1.vDerive[0].nChild, test1.vDerive[1].nChild};
    const auto derived{DeriveExtKey(master, path)};
    BOOST_REQUIRE(derived);
    BOOST_CHECK(EncodeExtKey(derived->first) == test1.vDerive[2].prv);

    KeyOriginInfo expected_origin;
    expected_origin.fingerprint = master.id_key_fingerprint();
    expected_origin.path = path;
    BOOST_CHECK(derived->second == expected_origin);

    const auto root{DeriveExtKey(master, {})};
    BOOST_REQUIRE(root);
    BOOST_CHECK(root->first == master);
    expected_origin.path.clear();
    BOOST_CHECK(root->second == expected_origin);

    CExtKey max_depth{master};
    for (auto i{0}; i++ < 255;) {
        CExtKey next_key;
        BOOST_REQUIRE(max_depth.Derive(next_key, 0));
        max_depth = next_key;
    }
    BOOST_CHECK(!DeriveExtKey(max_depth, {0}));
}

BOOST_AUTO_TEST_CASE(bip32_has_hardened_derivation)
{
    const std::vector<uint32_t> empty;
    const std::vector<uint32_t> unhardened{0, 1, 2};
    const std::vector<uint32_t> hardened{BIP32_HARDENED_FLAG};
    const std::vector<uint32_t> mixed{0, BIP32_HARDENED_FLAG | 1, 2};
    BOOST_CHECK(!HasHardenedDerivation(empty));
    BOOST_CHECK(!HasHardenedDerivation(unhardened));
    BOOST_CHECK(HasHardenedDerivation(hardened));
    BOOST_CHECK(HasHardenedDerivation(mixed));
}

BOOST_AUTO_TEST_CASE(bip32_max_depth) {
    CExtKey key_parent{DecodeExtKey(test1.vDerive[0].prv)}, key_child;
    CExtPubKey pubkey_parent{DecodeExtPubKey(test1.vDerive[0].pub)}, pubkey_child;

    // We can derive up to the 255th depth..
    for (auto i = 0; i++ < 255;) {
        BOOST_CHECK(key_parent.Derive(key_child, 0));
        std::swap(key_parent, key_child);
        BOOST_CHECK(pubkey_parent.Derive(pubkey_child, 0));
        std::swap(pubkey_parent, pubkey_child);
    }

    // But trying to derive a non-existent 256th depth will fail!
    BOOST_CHECK(key_parent.nDepth == 255);
    BOOST_CHECK(pubkey_parent.nDepth == 255);
    BOOST_CHECK(!key_parent.Derive(key_child, 0));
    BOOST_CHECK(!pubkey_parent.Derive(pubkey_child, 0));
}

BOOST_AUTO_TEST_CASE(parse_hd_keypath)
{
    std::vector<uint32_t> keypath;

    BOOST_CHECK(ParseHDKeypath("1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1", keypath));
    BOOST_CHECK(!ParseHDKeypath("///////////////////////////", keypath));

    BOOST_CHECK(ParseHDKeypath("1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1'/1", keypath));
    BOOST_CHECK(!ParseHDKeypath("//////////////////////////'/", keypath));

    BOOST_CHECK(ParseHDKeypath("1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/", keypath));
    BOOST_CHECK(!ParseHDKeypath("1///////////////////////////", keypath));

    BOOST_CHECK(ParseHDKeypath("1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1'/", keypath));
    BOOST_CHECK(!ParseHDKeypath("1/'//////////////////////////", keypath));

    BOOST_CHECK(ParseHDKeypath("", keypath));
    BOOST_CHECK(!ParseHDKeypath(" ", keypath));

    BOOST_CHECK(ParseHDKeypath("0", keypath));
    BOOST_CHECK(!ParseHDKeypath("O", keypath));

    BOOST_CHECK(ParseHDKeypath("0000'/0000'/0000'", keypath));
    BOOST_CHECK(!ParseHDKeypath("0000,/0000,/0000,", keypath));

    BOOST_CHECK(ParseHDKeypath("01234", keypath));
    BOOST_CHECK(!ParseHDKeypath("0x1234", keypath));

    BOOST_CHECK(ParseHDKeypath("1", keypath));
    BOOST_CHECK(!ParseHDKeypath(" 1", keypath));

    BOOST_CHECK(ParseHDKeypath("42", keypath));
    BOOST_CHECK(!ParseHDKeypath("m42", keypath));

    // A path element's numeric part is capped at 2^31-1; the top bit is
    // reserved for the hardened marker (h or ').
    BOOST_CHECK(ParseHDKeypath("2147483647", keypath));  // 0x7fffffff, largest normal index
    BOOST_CHECK(!ParseHDKeypath("2147483648", keypath)); // 0x80000000, would set the hardened bit
    BOOST_CHECK(!ParseHDKeypath("4294967295", keypath)); // 0xffffffff
    BOOST_CHECK(!ParseHDKeypath("4294967296", keypath)); // uint32_t max + 1

    BOOST_CHECK(ParseHDKeypath("m", keypath));
    BOOST_CHECK(!ParseHDKeypath("n", keypath));

    BOOST_CHECK(ParseHDKeypath("m/", keypath));
    BOOST_CHECK(!ParseHDKeypath("n/", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0", keypath));
    BOOST_CHECK(!ParseHDKeypath("n/0", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0'", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0''", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0h", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0hh", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0x", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0a", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0G", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/h0", keypath));

    keypath.clear();
    BOOST_REQUIRE(ParseHDKeypath("m/0h/1h/2h", keypath));
    BOOST_REQUIRE_EQUAL(keypath.size(), 3);
    BOOST_CHECK_EQUAL(keypath[0], BIP32_HARDENED_FLAG);
    BOOST_CHECK_EQUAL(keypath[1], BIP32_HARDENED_FLAG | 1);
    BOOST_CHECK_EQUAL(keypath[2], BIP32_HARDENED_FLAG | 2);

    BOOST_CHECK(ParseHDKeypath("m/0'/0'", keypath));
    BOOST_CHECK(ParseHDKeypath("m/0h/0h", keypath));
    BOOST_CHECK(ParseHDKeypath("m/0'/0h", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/'0/0'", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/h0/0'", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/0", keypath));
    BOOST_CHECK(!ParseHDKeypath("n/0/0", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/0/00", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0/0/f00", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/0/000000000000000000000000000000000000000000000000000000000000000000000000000000000000", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/1/1/111111111111111111111111111111111111111111111111111111111111111111111111111111111111", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/00/0", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0'/00/'0", keypath));

    BOOST_CHECK(ParseHDKeypath("m/1/", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/1//", keypath));

    // The cap applies to every element, wherever it sits in the path.
    BOOST_CHECK(ParseHDKeypath("m/2147483647", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/2147483648", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/4294967295", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/4294967296", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/2147483647", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0/2147483648", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0/4294967295", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0/4294967296", keypath));
}

BOOST_AUTO_TEST_SUITE_END()
