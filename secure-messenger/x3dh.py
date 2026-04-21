import nacl.signing
import nacl.public
import json
import hashlib
import requests

with open("client_keys.json") as f:
    alice_data = json.load(f)

alice_ik = nacl.signing.SigningKey(bytes.fromhex(alice_data["identity_private"]))
alice_ik_curve = alice_ik.to_curve25519_private_key()

BOB_ID = "ca7ae467f5dd9d0ecd70694ece7b3554aa57f8e2237907b60aebdb6db1666bb6"
response = requests.get(f"http://127.0.0.1:8000/fetch_bundle/{BOB_ID}")
bob_bundle = response.json()

used_opk_pub = bob_bundle["one_time_prekeys"][0]["public"]

bob_ik_curve_pub = nacl.signing.VerifyKey(bytes.fromhex(BOB_ID)).to_curve25519_public_key()
bob_spk_curve_pub = nacl.public.PublicKey(bytes.fromhex(bob_bundle["signed_prekey"]["public"]))
bob_opk_curve_pub = nacl.public.PublicKey(bytes.fromhex(used_opk_pub))

alice_ek = nacl.public.PrivateKey.generate()

dh1 = nacl.public.Box(alice_ik_curve, bob_spk_curve_pub).shared_key()
dh2 = nacl.public.Box(alice_ek, bob_ik_curve_pub).shared_key()
dh3 = nacl.public.Box(alice_ek, bob_spk_curve_pub).shared_key()
dh4 = nacl.public.Box(alice_ek, bob_opk_curve_pub).shared_key()

master_sk = dh1 + dh2 + dh3 + dh4
prk = hashlib.sha256(master_sk).digest()
shared_secret = hashlib.sha256(prk + b"X3DH for Secure Messenger Project").digest()

print("\n=== ALICE X3DH OUTPUT ===")
print(f"ALICE_EK_PUB: {alice_ek.public_key.encode().hex()}")
print(f"USED_BOB_OPK: {used_opk_pub}")
print(f"SHARED_SECRET: {shared_secret.hex()}")
