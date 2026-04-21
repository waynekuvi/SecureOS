from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

app = FastAPI()

# In-memory storage for the E2EE ecosystem
key_bundles = {}
message_store: Dict[str, List[dict]] = {}

class SignedPrekey(BaseModel):
    id: int
    public: str
    private: str
    signature: str

class OneTimePrekey(BaseModel):
    id: int
    public: str
    private: str

class Bundle(BaseModel):
    identity_public: str
    signed_prekey: SignedPrekey
    one_time_prekeys: List[OneTimePrekey]

class Message(BaseModel):
    sender_id: str
    receiver_id: str
    header: dict  # This carries the Ratchet Public Key!
    ciphertext: str

@app.post("/upload_bundle")
async def upload_bundle(bundle: Bundle):
    key_bundles[bundle.identity_public] = bundle.dict()
    print(f"✅ Bundle stored for: {bundle.identity_public[:8]}...")
    return {"status": "uploaded"}

@app.get("/fetch_bundle/{user_id}")
async def fetch_bundle(user_id: str):
    if user_id not in key_bundles:
        raise HTTPException(status_code=404, detail="User not found")
    
    bundle = key_bundles[user_id]
    if bundle['one_time_prekeys']:
        opk = bundle['one_time_prekeys'].pop(0)
        print(f"🔑 OPK consumed for: {user_id[:8]}...")
        return {
            "identity_public": bundle['identity_public'],
            "signed_prekey": bundle['signed_prekey'],
            "one_time_prekeys": [opk]
        }
    return bundle

@app.post("/send_message")
async def send_message(msg: Message):
    if msg.receiver_id not in message_store:
        message_store[msg.receiver_id] = []
    message_store[msg.receiver_id].append(msg.dict())
    print(f"📩 Encrypted message queued for: {msg.receiver_id[:8]}...")
    return {"status": "delivered to server"}

@app.get("/get_messages/{user_id}")
async def get_messages(user_id: str):
    msgs = message_store.get(user_id, [])
    message_store[user_id] = [] # Clear the mailbox
    print(f"📤 Mailbox emptied for: {user_id[:8]}...")
    return msgs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
