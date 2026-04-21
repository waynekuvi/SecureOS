import nacl.signing
import nacl.public
import json
import hashlib

with open("client_keys.json") as f:
    bob_data = json.load(f)

# === LATEST DATA FROM ALICE ===
alice_id_pub = "8ed6b1436f51b0ec39375d9aa252d98518f28f535d61ce629f5ff8b84afc849f"
alice_ek_pub = "09cd974cb610259d4893cf6f101f494b4107ec3c169b206860e85112c884cd53"
expected_secret = "6aa1379d142fe951dac004a3c0e26f34b5a0cfb5d8c58e2b7cf1ca19d859965a"
target_opk = "c164c906d39e186ceed29f02a959a473c9f06d07447d8ee1250fe6af4c18ea4b"

# Find the private key for the OPK Alice actually used
matching_priv = next((p["private"] for p in bob_data["one_time_prekeys"] if p["public"] == target_opk), None)

if not matching_priv:
    print("\n❌ ERROR: Bob's local file does not contain the OPK Alice fetched from the server.")
    print("This means the server is hosting an old bundle. Please restart the server and re-upload.")
    exit()

# Setup Keys
bob_ik = nacl.signing.SigningKey(bytes.fromhex(bob_data["identity_private"])).to_curve25519_private_key()
bob_spk = nacl.public.PrivateKey(bytes.fromhex(bob_data["signed_prekey"]["private"]))
bob_opk = nacl.public.PrivateKey(bytes.fromhex(matching_priv))

alice_ik_curve_pub = nacl.signing.VerifyKey(bytes.fromhex(alice_id_pub)).to_curve25519_public_key()
alice_ek_curve_pub = nacl.public.PublicKey(bytes.fromhex(alice_ek_pub))

# 4 DHs
dh1 = nacl.public.Box(bob_spk, alice_ik_curve_pub).shared_key()
dh2 = nacl.public.Box(bob_ik, alice_ek_curve_pub).shared_key()
dh3 = nacl.public.Box(bob_spk, alice_ek_curve_pub).shared_key()
dh4 = nacl.public.Box(bob_opk, alice_ek_curve_pub).shared_key()

master_sk = dh1 + dh2 + dh3 + dh4
prk = hashlib.sha256(master_sk).digest()
shared_secret = hashlib.sha256(prk + b"X3DH for Secure Messenger Project").digest()

print(f"\nCalculated: {shared_secret.hex()}")
if shared_secret.hex() == expected_secret:
    print("✅ MATCH! Secure channel established.")
else:
    print("❌ STILL NO MATCH. Order of DH or Identity Key mismatch.")
