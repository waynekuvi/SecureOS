import hashlib
from nacl.secret import SecretBox

# Simplified KDF chain (Signal uses HMAC-based KDF – this is SHA256 chain for demo)
def kdf_chain(chain_key: bytes) -> tuple[bytes, bytes]:
    # Advance chain key and derive message key
    new_chain_key = hashlib.sha256(chain_key + b"chain_step").digest()
    message_key = hashlib.sha256(chain_key + b"message_key").digest()
    return new_chain_key, message_key

class RatchetState:
    def __init__(self, root_key: bytes):
        self.chain_key = root_key
        self.message_num = 0

    def ratchet_step(self) -> bytes:
        self.chain_key, mk = kdf_chain(self.chain_key)
        self.message_num += 1
        return mk

# Encryption/Decryption (SecretBox = AES-GCM, fixed nonce for demo reproducibility – real: random nonce + include in message)
def encrypt_message(message_key: bytes, plaintext: bytes) -> bytes:
    box = SecretBox(message_key)
    nonce = b"\x00" * 24  # FIXED for demo – NEVER do this in production!
    return box.encrypt(plaintext, nonce)

def decrypt_message(message_key: bytes, ciphertext: bytes) -> bytes:
    box = SecretBox(message_key)
    nonce = b"\x00" * 24
    return box.decrypt(ciphertext)
