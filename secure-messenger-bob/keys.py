import nacl.signing
import nacl.public
import json

ik_private = nacl.signing.SigningKey.generate()
ik_public = ik_private.verify_key
spk_private = nacl.public.PrivateKey.generate()
spk_public = spk_private.public_key
signature = ik_private.sign(spk_public.encode())

otps = []
for i in range(5):
    otp_priv = nacl.public.PrivateKey.generate()
    otps.append({
        "id": i,
        "public": otp_priv.public_key.encode().hex(),
        "private": otp_priv.encode().hex()
    })

keys = {
    "identity_public": ik_public.encode().hex(),
    "identity_private": ik_private.encode().hex(),
    "signed_prekey": {
        "id": 1,
        "public": spk_public.encode().hex(),
        "private": spk_private.encode().hex(),
        "signature": signature.signature.hex()
    },
    "one_time_prekeys": otps
}

with open("client_keys.json", "w") as f:
    json.dump(keys, f, indent=4)

print(f"NEW IDENTITY PUB: {keys['identity_public']}")
