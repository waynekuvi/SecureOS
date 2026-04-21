# SecureOS

A Python implementation of the Signal Protocol — X3DH key agreement and the Double Ratchet algorithm — built with `pynacl` (libsodium bindings). Includes a FastAPI key server, two client simulations, and an interactive Streamlit visualizer.

---

## Overview

SecureOS demonstrates end-to-end encrypted messaging from first principles. It covers the full lifecycle of a secure session: key generation, bundle publication, X3DH handshake, shared secret derivation, and per-message Double Ratchet encryption with forward secrecy.

The project is structured across three modules:

| Module | Purpose |
|---|---|
| `secure-messenger` | Alice-side client, key server, X3DH initiator, ratchet engine |
| `secure-messenger-bob` | Bob-side responder, bundle upload, X3DH verification |
| `secure-messenger-visualizer` | Interactive Streamlit UI for visualising the Double Ratchet in real time |

---

## Cryptographic Design

### X3DH Key Agreement (Extended Triple Diffie-Hellman)

On session initiation, four Diffie-Hellman operations are performed between Alice and Bob's key material:

```
DH1 = Box(Alice_IK_curve, Bob_SPK)
DH2 = Box(Alice_EK,       Bob_IK_curve)
DH3 = Box(Alice_EK,       Bob_SPK)
DH4 = Box(Alice_EK,       Bob_OPK)

master_sk     = DH1 || DH2 || DH3 || DH4
prk           = SHA-256(master_sk)
shared_secret = SHA-256(prk || "X3DH for Secure Messenger Project")
```

Both parties independently derive the same `shared_secret` without transmitting it. The one-time prekey (OPK) is consumed on use and deleted from the server, preventing replay.

### Key Types

| Key | Algorithm | Purpose |
|---|---|---|
| Identity Key (IK) | Ed25519 | Long-term identity, converted to Curve25519 for DH |
| Signed Prekey (SPK) | X25519 | Medium-term key, signed by IK |
| One-Time Prekey (OPK) | X25519 | Single-use, provides forward secrecy on first message |
| Ephemeral Key (EK) | X25519 | Per-session, generated fresh by initiator |

### Double Ratchet

After X3DH, the shared secret seeds a KDF chain. Each message advances the chain, deriving a fresh message key:

```
chain_key[n+1] = SHA-256(chain_key[n] || "chain_step")
message_key[n] = SHA-256(chain_key[n] || "message_key")
```

Messages are encrypted with `SecretBox` (XSalsa20-Poly1305). Compromise of a message key does not expose past or future keys.

---

## Project Structure

```
SecureOS_ProjectFiles/
├── secure-messenger/
│   ├── server.py           # FastAPI key distribution server
│   ├── keys.py             # Key generation (Ed25519 + X25519)
│   ├── x3dh.py             # Alice-side X3DH handshake
│   ├── ratchet.py          # Double Ratchet KDF chain + encryption
│   ├── send_message.py     # Encrypt and send messages (Alice)
│   ├── receive_message.py  # Decrypt received messages (Bob)
│   ├── app.py              # Streamlit X3DH handshake UI (Alice)
│   └── client_keys.json    # Alice's generated key material
│
├── secure-messenger-bob/
│   ├── keys.py             # Bob's key generation
│   ├── upload_bundle.py    # Publishes Bob's bundle to the server
│   ├── bob_responder.py    # Bob-side X3DH verification
│   └── client_keys.json    # Bob's generated key material
│
└── secure-messenger-visualizer/
    ├── app.py              # Interactive Double Ratchet visualizer
    └── client_keys.json    # Visualizer session keys
```

---

## Requirements

```
fastapi
uvicorn
pynacl
requests
streamlit
```

Install all dependencies:

```bash
pip install fastapi uvicorn pynacl requests streamlit
```

---

## Running the System

### 1. Start the Key Server

```bash
cd secure-messenger
python server.py
```

The server runs at `http://127.0.0.1:8000`. It handles bundle uploads, bundle fetches (consuming OPKs), and encrypted message queuing.

### 2. Generate Bob's Keys and Upload His Bundle

```bash
cd secure-messenger-bob
python keys.py
python upload_bundle.py
```

`upload_bundle.py` posts Bob's identity key, signed prekey, and one-time prekeys to the server. Copy the printed identity public key — Alice needs it to initiate the handshake.

### 3. Generate Alice's Keys

```bash
cd secure-messenger
python keys.py
```

### 4. Perform the X3DH Handshake (Alice)

Open `x3dh.py` and set `BOB_ID` to Bob's identity public key, then run:

```bash
python x3dh.py
```

Expected output:

```
=== ALICE X3DH OUTPUT ===
ALICE_EK_PUB: <hex>
USED_BOB_OPK: <hex>
SHARED_SECRET: <hex>
```

### 5. Verify the Shared Secret (Bob)

Open `secure-messenger-bob/bob_responder.py` and set:

```python
alice_id_pub    = "<Alice's identity public key>"
alice_ek_pub    = "<ALICE_EK_PUB from step 4>"
expected_secret = "<SHARED_SECRET from step 4>"
target_opk      = "<USED_BOB_OPK from step 4>"
```

Then run:

```bash
cd secure-messenger-bob
python bob_responder.py
```

A successful handshake prints:

```
Calculated: <hex>
MATCH. Secure channel established.
```

### 6. Exchange Encrypted Messages

**Alice sends:**

```bash
cd secure-messenger
python send_message.py
```

Output:

```
Sent: Hello Bob!
Ciphertext (hex): 000000...

Sent: This is secure!
Ciphertext (hex): 000000...

Sent: Forward secrecy achieved.
Ciphertext (hex): 000000...
```

**Bob decrypts:**

Paste the ciphertexts into `receive_message.py`, then run:

```bash
python receive_message.py
```

Output:

```
Message 1: Hello Bob!
Message 2: This is secure!
Message 3: Forward secrecy achieved.
```

---

## Protocol Visualizer

The visualizer provides a live, three-column interface showing Alice's terminal, the network observer (ciphertext in transit), and Bob's decrypted output. It also exposes DH ratchet rotation.

```bash
cd secure-messenger-visualizer
streamlit run app.py
```

Open `http://localhost:8501` in a browser. Use the sidebar to trigger a DH ratchet rotation and observe the root key and chain state update in real time.

---

## Server API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload_bundle` | Publish a user's key bundle |
| `GET` | `/fetch_bundle/{user_id}` | Fetch a bundle and consume one OPK |
| `POST` | `/send_message` | Queue an encrypted message |
| `GET` | `/get_messages/{user_id}` | Retrieve and clear the mailbox |

---

## Security Notes

This implementation is a protocol demonstration. The following deviations from production Signal apply:

- **Fixed nonces** — `ratchet.py` uses a zeroed 24-byte nonce for `SecretBox`. Production systems must generate a random nonce per message and include it in the ciphertext header.
- **In-memory server** — key bundles and messages are stored in Python dicts. A production server requires persistent, authenticated storage.
- **No DH ratchet step** — only the symmetric KDF chain is advanced per message. Full Double Ratchet includes an asymmetric DH ratchet step when the conversation direction changes.
- **Key material in JSON** — private keys are stored in plaintext `client_keys.json` files for demonstration. Production clients use platform secure enclaves or encrypted key stores.

---

## References

- [The X3DH Key Agreement Protocol — Marlinspike & Perrin, Signal](https://signal.org/docs/specifications/x3dh/)
- [The Double Ratchet Algorithm — Marlinspike & Perrin, Signal](https://signal.org/docs/specifications/doubleratchet/)
- [PyNaCl Documentation](https://pynacl.readthedocs.io/)
