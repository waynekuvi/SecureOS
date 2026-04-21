import os
import json
from nacl.signing import SigningKey
from nacl.public import PrivateKey

KEYS_FILE = "client_keys.json"

def generate_keys():
    # Identity key (Ed25519)
    identity = SigningKey.generate()
    identity_private_seed = identity.encode().hex()  # 32-byte seed
    identity_public = identity.verify_key.encode().hex()

    # Signed prekey (X25519)
    signed_prekey = PrivateKey.generate()
    signed_prekey_private = signed_prekey.encode().hex()
    signed_prekey_public = signed_prekey.public_key.encode().hex()
    signature = identity.sign(bytes.fromhex(signed_prekey_public)).signature.hex()

    # 10 one-time prekeys (X25519)
    one_time_prekeys = []
    for i in range(10):
        otpk = PrivateKey.generate()
        one_time_prekeys.append({
            "id": i,
            "public": otpk.public_key.encode().hex(),
            "private": otpk.encode().hex()  # Saved locally only
        })

    keys = {
        "identity_private": identity_private_seed,  # seed only – full SK reconstructed later
        "identity_public": identity_public,
        "signed_prekey_private": signed_prekey_private,
        "signed_prekey": {
            "id": 1,
            "public": signed_prekey_public,
            "signature": signature
        },
        "one_time_prekeys": one_time_prekeys
    }

    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

    print("Keys generated and saved to", KEYS_FILE)
    print("Identity public key (share this):", keys["identity_public"])

if not os.path.exists(KEYS_FILE):
    generate_keys()
else:
    print("Keys already exist in", KEYS_FILE)
    with open(KEYS_FILE) as f:
        keys = json.load(f)
        print("Identity public key:", keys["identity_public"])
