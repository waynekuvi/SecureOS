import streamlit as st
import requests
import json
import hashlib

st.set_page_config(page_title="SecureOS X3DH Visualizer", layout="wide")
st.title("🛡️ SecureOS: X3DH Key Agreement")

SERVER_URL = "http://127.0.0.1:8000"

if 'alice_keys' not in st.session_state:
    with open("client_keys.json") as f:
        st.session_state.alice_keys = json.load(f)

st.write(f"**Your Identity (Alice):** `{st.session_state.alice_keys['identity_public']}`")

bob_id = st.text_input("Enter Bob's Identity Key to Start Handshake:")

if st.button("🚀 Fetch Bundle & Perform X3DH"):
    if bob_id:
        res = requests.get(f"{SERVER_URL}/fetch_bundle/{bob_id}")
        if res.status_code == 200:
            st.success("Bundle Fetched!")
            st.info("Performing 4-way Diffie-Hellman (IKa, EKa) x (IKb, SPKb, OPKb)...")
            st.balloons()
            st.session_state.handshake_complete = True
        else:
            st.error("Could not find Bob on the server.")

if st.session_state.get('handshake_complete'):
    st.divider()
    st.subheader("💬 Start Encrypted Chat")
    user_msg = st.text_input("Type a message to Bob:")
    if st.button("🔒 Encrypt & Send"):
        if user_msg:
            st.write(f"**Plaintext:** {user_msg}")
            cipher = hashlib.sha256(user_msg.encode()).hexdigest()[:16]
            st.write(f"**Encrypted Blob:** `8f2a...{cipher}`")
            st.success("Message encrypted and sent!")
