import json
import requests

with open("client_keys.json") as f:
    keys = json.load(f)

bundle_data = {
    "identity_public": keys["identity_public"],
    "signed_prekey": keys["signed_prekey"],
    "one_time_prekeys": keys["one_time_prekeys"]
}

response = requests.post("http://127.0.0.1:8000/upload_bundle", json=bundle_data)
if response.status_code == 200:
    print(f"✅ Success! Bob's bundle uploaded.")
    print(f"Identity Key: {keys['identity_public']}")
else:
    print(f"❌ Error: {response.text}")
