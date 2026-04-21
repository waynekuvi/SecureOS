import ratchet

# Same shared secret as Alice used
shared_secret = bytes.fromhex("59c3b61a87bacf2e6887cb548cb7276b1e120ffa92294c553b6b6813a9b8dfee")

bob_ratchet = ratchet.RatchetState(shared_secret)

# ← Paste the three ciphertexts you got from send_message.py
ciphertexts = [
    "000000000000000000000000000000000000000000000000ea9c253a2c8ea617a2594a29fe836bb07fa4ad67ef450a499fa7",
    "000000000000000000000000000000000000000000000000251e4b570f5ed4dff2bb757ff6808ea2ea065b34ba07d4fe9d608ce473558f",
    "0000000000000000000000000000000000000000000000002d1db585e13585b5433edaf973479ef771a78aa5e80c75cf55837a994211724e65632e9a25fb4c7099"
]

for i, ct_hex in enumerate(ciphertexts, 1):
    ct = bytes.fromhex(ct_hex)
    mk = bob_ratchet.ratchet_step()
    try:
        plaintext = ratchet.decrypt_message(mk, ct)
        print(f"Message {i}: {plaintext.decode('utf-8')}")
    except Exception as e:
        print(f"Decryption failed on message {i}: {e}")
