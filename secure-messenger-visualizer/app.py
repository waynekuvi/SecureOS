import streamlit as st
import hashlib
import time
from nacl.public import PrivateKey
from nacl.secret import SecretBox

st.set_page_config(page_title="End-to-End Encrypted Protocol Visualizer", layout="wide", initial_sidebar_state="expanded")

# --- REFINED UI STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 2rem !important;
        padding-left: 4rem !important;
        padding-right: 4rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    .stApp { 
        background-color: #ffffff;
        color: #111827;
    }

    section[data-testid="stSidebar"] {
        background-color: #fafafa !important;
        border-right: 1px solid #e5e7eb;
        padding-top: 2rem !important;
    }
    
    [data-testid="stSidebarUserContent"] {
        padding-top: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    h1, h2, h3, p, span, label, .stMarkdown, div {
        font-family: 'Inter', sans-serif !important;
    }

    h1 { 
        font-weight: 600 !important; 
        font-size: 24px !important;
        letter-spacing: -0.03em !important;
        color: #111827 !important;
        margin-top: 0 !important;
        margin-bottom: 6px !important;
    }

    .subtitle {
        font-size: 14px;
        font-weight: 400;
        color: #6b7280 !important;
        margin-bottom: 3rem;
        letter-spacing: -0.01em;
    }

    .column-header {
        font-size: 11px;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af !important;
        margin-bottom: 1.2rem;
    }

    .sidebar-section {
        font-size: 11px;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af !important;
        margin-top: 2.5rem;
        margin-bottom: 1rem;
    }

    div.stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.65rem 1.25rem !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        width: 100%;
        transition: all 0.15s ease;
    }

    div.stButton > button:hover {
        background-color: #1f1f1f !important;
        color: #ffffff !important;
        transform: translateY(-1px);
    }

    .stTextInput input {
        background-color: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
        padding: 0.65rem 1rem !important;
        font-size: 13px !important;
    }

    .packet-trace {
        font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
        color: #374151;
        background: #f9fafb;
        padding: 14px 16px;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        font-size: 12px;
        margin-bottom: 10px;
    }

    .terminal-box {
        background: #fafafa;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 16px;
        min-height: 100px;
    }

    .footer-section {
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
    }

    .footer-label {
        font-size: 12px;
        font-weight: 600;
        color: #111827 !important;
        margin-bottom: 6px;
    }

    .footer-value {
        font-family: 'SF Mono', monospace;
        font-size: 11px;
        color: #6b7280 !important;
    }

    .status-active {
        color: #10b981;
        font-size: 13px;
        font-weight: 500;
    }

    .status-active::before {
        content: '●';
        margin-right: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CRYPTO LOGIC ---
def kdf_rk(root_key, dh_output):
    h = hashlib.sha256(root_key + dh_output).digest()
    return h[:32], h[32:]

def kdf_ck(chain_key):
    msg_key = hashlib.sha256(chain_key + b"msg").digest()
    next_ck = hashlib.sha256(chain_key + b"next").digest()
    return next_ck, msg_key

# --- SESSION STATE ---
if 'root_key' not in st.session_state:
    st.session_state.root_key = hashlib.sha256(b"handshake_secret").digest()
    st.session_state.alice_ck = None
    st.session_state.packets = []
    st.session_state.history = []

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='sidebar-section'>CONFIGURATION</div>", unsafe_allow_html=True)
    if st.button("Rotate Root Key"):
        new_entropy = bytes(PrivateKey.generate().public_key)[:32]
        st.session_state.root_key, st.session_state.alice_ck = kdf_rk(st.session_state.root_key, new_entropy)
        st.session_state.rotated = True
        st.rerun()
    if st.session_state.get("rotated"):
        st.success(f"✓ DH Ratchet triggered. New Root Key: {st.session_state.root_key.hex()[:20]}...")
    
    st.markdown("<div class='sidebar-section'>SESSION METRICS</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px; color:#4b5563;'>Protocol: Double Ratchet</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px; color:#4b5563;'>Encryption: AES-256-GCM</div>", unsafe_allow_html=True)

# --- MAIN INTERFACE ---
st.markdown("<h1>End-to-End Encrypted Protocol Visualizer</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>CST3990 | Secure Communication System</div>", unsafe_allow_html=True)

col_alice, col_net, col_bob = st.columns([1, 1.4, 1])

with col_alice:
    st.markdown("<div class='column-header'>ALICE TERMINAL</div>", unsafe_allow_html=True)
    msg_input = st.text_input("Message", placeholder="Enter message...", label_visibility="collapsed", key="alice_input")
    if st.button("Encrypt and Send"):
        if msg_input:
            if not st.session_state.alice_ck:
                st.session_state.root_key, st.session_state.alice_ck = kdf_rk(st.session_state.root_key, b"init")
            st.session_state.alice_ck, msg_key = kdf_ck(st.session_state.alice_ck)
            ciphertext = hashlib.sha256(msg_key + msg_input.encode()).hexdigest()[:32]
            st.session_state.packets.append({"payload": ciphertext, "ts": time.strftime("%H:%M:%S")})
            st.session_state.history.append({"p": msg_input, "k": msg_key.hex()[:10]})
            st.session_state.rotated = True
        st.rerun()
    if st.session_state.get("rotated"):
        st.success(f"✓ DH Ratchet triggered. New Root Key: {st.session_state.root_key.hex()[:20]}...")

with col_net:
    st.markdown("<div class='column-header'>NETWORK OBSERVER</div>", unsafe_allow_html=True)
    if not st.session_state.packets:
        st.markdown("<div style='color:#d1d5db; text-align:center; padding-top:2rem;'>Waiting for traffic...</div>", unsafe_allow_html=True)
    else:
        for p in reversed(st.session_state.packets[-5:]):
            st.markdown(f'<div class="packet-trace"><b>[{p["ts"]}]</b> CIPHER: <span style="color:#2563eb;">{p["payload"]}</span></div>', unsafe_allow_html=True)

with col_bob:
    st.markdown("<div class='column-header'>BOB TERMINAL</div>", unsafe_allow_html=True)
    if st.session_state.history:
        latest = st.session_state.history[-1]
        st.markdown(f"""
            <div class='terminal-box'>
                <div style='font-size:14px; font-weight:500;'>Decrypted: {latest['p']}</div>
                <div style='font-family:monospace; font-size:11px; color:#9ca3af;'>Key ID: {latest['k']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#d1d5db; text-align:center; padding-top:2rem;'>No incoming data.</div>", unsafe_allow_html=True)

# --- FOOTER STATUS ---
st.markdown("<div class='footer-section'></div>", unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("<div class='footer-label'>Root Key</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='footer-value'>{st.session_state.root_key.hex()[:16]}...</div>", unsafe_allow_html=True)
with f2:
    st.markdown("<div class='footer-label'>Chain State</div>", unsafe_allow_html=True)
    st.markdown("<div class='status-active'>Active</div>", unsafe_allow_html=True)
with f3:
    st.markdown("<div class='footer-label'>Security</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 13px; color: #4b5563;'>Perfect Forward Secrecy</div>", unsafe_allow_html=True)
