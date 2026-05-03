# Cell 1 — Install libraries
!pip install streamlit groq pyngrok -q
print("Installation complete!")

# Cell 2 — Complete working app.py
app_code = '''
import streamlit as st
from groq import Groq

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="HDFC FinBot",
    page_icon="🏦",
    layout="centered"
)

# ── STYLING ──
st.markdown("""
<style>
    .stTextInput > div > div > input {
        background-color: #0F2B4A;
        color: white;
        border: 1px solid #1D9E75;
        border-radius: 10px;
    }
    .stButton > button {
        background-color: #1D9E75;
        color: white;
        border-radius: 10px;
        border: none;
        width: 100%;
        font-weight: bold;
        height: 45px;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ──
st.markdown("""
<div style="background:#1B3A6B; padding:20px;
border-radius:12px; text-align:center;
margin-bottom:20px;">
    <h1 style="color:white; margin:0;">
        🏦 FinBot
    </h1>
    <p style="color:#9FE1CB; margin:0;">
        HDFC Bank AI Assistant
    </p>
    <p style="color:#5DCAA5; font-size:12px;">
        NEFT | RTGS | SFMS Support
    </p>
</div>
""", unsafe_allow_html=True)

# ── POLICY DOCUMENT ──
neft_policy = """
HDFC BANK NEFT & RTGS POLICY 2026

NEFT:
- Operates 24x7 including Sundays and holidays
- Minimum: Re. 1, Maximum: No limit
- Settlement in 30-minute batches, 48 per day
- Free for savings account holders
- Needs: Account number, IFSC code

RTGS:
- Operates 24x7 including Sundays and holidays
- Minimum: Rs. 2,00,000, Maximum: No limit
- Real-time settlement within 30 minutes
- Free for savings account holders
- Best for large urgent transfers

FAILED TRANSACTIONS:
- Refund within 2 hours
- SMS and email notification sent
- Visit branch or raise support ticket
- Team responds within 24 working hours

DAILY LIMITS:
- Internet banking: Rs. 10 lakhs NEFT
- Mobile banking: Rs. 5 lakhs NEFT
- Branch: No daily limit

IFSC CODE:
- 11 character code
- First 4: Bank code, 5th: Always 0
- Last 6: Branch code
"""

# ── GROQ CLIENT ──
client = Groq(api_key="your-groq-key-here")

# ── SYSTEM PROMPT ──
system_prompt = f"""
You are Charan Sai, a friendly Senior IT Engineer
at HDFC Bank, Madhapur, Hyderabad.
Answer questions about NEFT, RTGS and SFMS ONLY
using the policy document below.
If answer is not in the document, say you will
check and follow up.

POLICY DOCUMENT:
{neft_policy}

Rules:
- Always be friendly and professional
- Never disclose other customer details
- Always end with: Is there anything else 
  I can help you?
"""

# ── INITIALIZE SESSION STATE ──
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am Charan Sai from HDFC Bank. How can I help you with NEFT, RTGS or SFMS today? Is there anything else I can help you?"
    })

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

if "pending_message" not in st.session_state:
    st.session_state.pending_message = ""

# ── PROCESS PENDING MESSAGE ──
def process_message(user_msg):
    if not user_msg.strip():
        return

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_msg
    })

    # Build API messages
    api_messages = [
        {"role": "system", "content": system_prompt}
    ] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Call Groq API
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=api_messages
    )
    reply = response.choices[0].message.content

    # Add FinBot reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # Clear input
    st.session_state.input_key += 1
    st.session_state.pending_message = ""

# ── CHECK FOR PENDING MESSAGE ──
if st.session_state.pending_message:
    process_message(st.session_state.pending_message)

# ── DISPLAY CHAT HISTORY ──
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="display:flex;
        justify-content:flex-end; margin:8px 0;">
            <div style="background:#1B3A6B;
            color:white; padding:10px 16px;
            border-radius:18px 18px 4px 18px;
            max-width:75%; font-size:14px;">
                {msg["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex;
        justify-content:flex-start;
        margin:8px 0; align-items:flex-start;">
            <div style="background:#1D9E75;
            color:white; border-radius:50%;
            width:32px; height:32px;
            display:flex; align-items:center;
            justify-content:center;
            margin-right:8px; font-size:14px;
            flex-shrink:0;">🏦</div>
            <div style="background:#0F2B4A;
            color:#9FE1CB; padding:10px 16px;
            border-radius:4px 18px 18px 18px;
            max-width:75%; font-size:14px;
            border:1px solid #1D9E75;">
                {msg["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── INPUT AREA ──
# ── INITIALIZE ──
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "last_processed" not in st.session_state:
    st.session_state.last_processed = ""
if "saved_input" not in st.session_state:
    st.session_state.saved_input = ""

# ── SAVE INPUT ON EVERY KEYSTROKE ──
def save_input():
    st.session_state.saved_input = st.session_state.get(
        f"user_input_{st.session_state.input_key}", ""
    )

# ── INPUT AREA ──
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Ask about NEFT, RTGS, SFMS...",
        label_visibility="collapsed",
        key=f"user_input_{st.session_state.input_key}",
        on_change=save_input  # saves on every change
    )

with col2:
    send_clicked = st.button("Send 📤")

# ── DETERMINE WHAT TO PROCESS ──
# Enter key → user_input has value
# Send button → use saved_input
message_to_process = ""

if user_input and \
   user_input != st.session_state.last_processed:
    # Enter key pressed
    message_to_process = user_input

elif send_clicked and \
     st.session_state.saved_input and \
     st.session_state.saved_input != \
     st.session_state.last_processed:
    # Send button clicked
    message_to_process = st.session_state.saved_input

# ── PROCESS MESSAGE ──
if message_to_process:

    # Mark as processed
    st.session_state.last_processed = message_to_process

    # Clear input
    st.session_state.input_key += 1
    st.session_state.saved_input = ""

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": message_to_process
    })

    # Build API messages
    api_messages = [
        {"role": "system", "content": system_prompt}
    ] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Call Groq API
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=api_messages
    )
    reply = response.choices[0].message.content

    # Add FinBot reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    st.rerun()

# ── FOOTER ──
st.markdown("""
<div style="text-align:center; margin-top:30px;
color:#3A6A5A; font-size:11px;">
    Built by Charan Sai N · AI Career Accelerator
    Week 1 · 2026
</div>
""", unsafe_allow_html=True)
'''

# Save app.py
with open("app.py", "w") as f:
    f.write(app_code)

print("app.py saved successfully!")


# Cell 3 — Clean restart (kills old tunnels first!)
from pyngrok import ngrok
import subprocess
import time

# Step 1 — Kill ALL old tunnels and processes
print("Cleaning up old tunnels...")
ngrok.kill()  # kills all existing ngrok tunnels
time.sleep(2)

# Step 2 — Kill old Streamlit if running
subprocess.run(
    ["pkill", "-f", "streamlit"],
    capture_output=True
)
time.sleep(2)
print("Cleanup done!")

# Step 3 — Set your ngrok token
ngrok.set_auth_token("your-ngroq-auth-here")

# Step 4 — Start fresh Streamlit
process = subprocess.Popen([
    "streamlit", "run", "app.py",
    "--server.port=8501",
    "--server.headless=true"
])
time.sleep(5)
print("Streamlit started!")

# Step 5 — Create ONE clean tunnel
public_url = ngrok.connect(8501)
print("=" * 50)
print("FinBot Web App is LIVE!")
print(f"Open this link: {public_url}")
print("=" * 50)
