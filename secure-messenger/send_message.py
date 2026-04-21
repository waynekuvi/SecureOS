import ratchet
import json

# Load X3DH shared secret (from previous run – hardcode for demo)
shared_secret = bytes.fromhex("59c3b61a87bacf2e6887cb548cb7276b1e120ffa92294c553b6b6813a9b8dfee")  # From your last run

# Alice's sending ratchet
alice_ratchet = ratchet.RatchetState(shared_secret)

messages = ["Hello Bob!", "This is secure!", "Forward secrecy achieved."]

for msg in messages:
    mk = alice_ratchet.ratchet_step()
    ciphertext = ratchet.encrypt_message(mk, msg.encode())
    print(f"Sent: {msg}")
    print(f"Ciphertext (hex): {ciphertext.hex()}\n")
