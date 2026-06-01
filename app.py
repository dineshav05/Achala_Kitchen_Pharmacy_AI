import streamlit as st
from PIL import Image
from openai import OpenAI

# 1. Initialize the OpenAI Client Safely
# This tells the code to look for the key in Streamlit's secure dashboard, NOT in the code.
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("API Key not found. Please set it up in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# 2. UI Configuration
# 1. Load your custom logo image

# 2. Function to securely encode your logo for the web UI
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# 2. Update the page configuration to use the image as the browser tab icon
st.set_page_config(
    page_title="Achala Digital Vaidya: Kitchen Pharmacy AI", 
    page_icon=logo, 
    layout="centered"
)
# Make sure "Achala_DV_1.png" is in the same directory as this script
logo = Image.open("Achala_Digital_Vaidya.png")

# 3. The Responsive HTML/CSS Header
# This Flexbox design forces the logo and text to stay perfectly centered on all screen sizes
responsive_header = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 10px;">
        <img src="data:image/png;base64,{logo_base64}" width="90" style="margin-bottom: 15px;">
        <h1 style="margin: 0; padding: 0; line-height: 1.2;">Achala Digital Vaidya:<br>Kitchen Pharmacy AI</h1>
        <p style="color: #888888; font-size: 0.95rem; margin-top: 10px; margin-bottom: 20px;">
            A smart health advisor based on Rajiv Dixit's Ayurvedic principles for joint and back pain.
        </p>
    </div>
    <hr style="margin-bottom: 30px;">
"""

# Inject the custom responsive header into the app
st.markdown(responsive_header, unsafe_allow_html=True)

# 3. Create a custom layout with vertical alignment
# The vertical_alignment="center" perfectly aligns the image with the middle of the title
col1, col2 = st.columns([1, 8], vertical_alignment="center")

with col1:
    # Display the image and adjust the width to align nicely with the text
    # Increased slightly to 130 to balance the longer title
    st.image(logo, width=200) 

with col2:
    # Display the exact title from your screenshot
    st.title("Achala Digital Vaidya: Kitchen Pharmacy AI")
st.caption("A smart health advisor based on Rajiv Dixit's Ayurvedic principles for joint and back pain.")
st.write("---")

# 3. The Core Knowledge System Prompt
SYSTEM_PROMPT = """You are Rajiv Dixit AI, an expert consultant in Ayurveda and Vata-induced joint pain. Your goal is to help the common man reverse chronic back and joint pain using accessible, budget-friendly kitchen remedies.

Follow these rules strictly:
1. Identify if the user's symptoms point to a Vata imbalance (e.g., cracking joints, long morning stiffness, shifting body pain).
2. Recommend affordable home remedies based on Rajiv Dixit's protocols:
   - Chronic/Autoimmune/Rheumatoid Arthritis -> Parijat (Harsingar) leaf decoction.
   - Calcium Deficiency / Post-Menopause / Bone weakness -> Edible Limestone (Chuna), wheat-grain size mixed in curd, dal, or warm water once daily.
   - General Stiffness -> Half a teaspoon of soaked Methi Dana (Fenugreek seeds) overnight, chewed on an empty stomach.
3. SAFETY GUARDRAIL: You MUST explicitly check if the user has a history of kidney stones or gallstones BEFORE recommending Chuna (Edible Limestone). If they answer yes, strictly forbid Chuna.
4. Enforce foundational lifestyle rules: sit down while drinking water (sip by sip), completely eliminate refined oils, and avoid highly sour/acidic foods.
5. Keep your tone compassionate, simple, and professional. Respond naturally in the exact language or script the user uses (Hindi, Hinglish, English, etc.).
"""

# 4. Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# 5. Display Past Messages (Skipping the hidden system prompt)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

import base64

# 1. Initialize states for payment tracking
if "premium_unlocked" not in st.session_state:
    st.session_state.premium_unlocked = False
if "show_qr" not in st.session_state:
    st.session_state.show_qr = False

# --- THE FIX: Initialize the variable as empty for free users ---
uploaded_file = None

st.write("### 🔍 Advanced Diagnostic Analysis")

# 2. Check if the user has paid
if not st.session_state.premium_unlocked:
    st.info("🔒 **Premium Feature:** Upload a photo of your joint or a medical report for deep visual analysis and tailored dietary matching.")
    if not st.session_state.show_qr:
        pay_col, info_col = st.columns([1, 2], vertical_alignment="center")
        with pay_col:
            if st.button("Unlock Feature (₹49)"):
                st.session_state.show_qr = True
                st.rerun()
        with info_col:
            st.caption("⚡ One-time fee per analysis. Pay securely via any UPI App (GPay, PhonePe, Paytm).")
            
    else:
        qr_col, text_col = st.columns([1, 1])
        with qr_col:
            st.image("QRCODE.jpeg", width=250)
        with text_col:
            st.write("### Complete Your Payment")
            st.write("1. Open **GPay, PhonePe, or Paytm** on your phone.")
            st.write("2. Scan the QR code or send **₹49** directly to:")
            st.code("dinesha.vishwanatha05-2@okaxis")
            
            st.write("---")
            st.write("### 🔐 Verify Transaction")
            
            # Form forces the input before execution
            with st.form("payment_verification_form"):
                utr_input = st.text_input(
                    "Enter 12-Digit UPI Ref No. / UTR ID:", 
                    placeholder="e.g., 3145XXXXXXXX",
                    max_chars=12
                )
                submit_verification = st.form_submit_button("Submit & Unlock Dashboard")
                
                if submit_verification:
                    # Clean up the input text
                    clean_utr = utr_input.strip()
                    
                    # Basic Validation: Ensure it is a 12-digit number common to Indian UPI systems
                    if len(clean_utr) == 12 and clean_utr.isdigit():
                        st.session_state.premium_unlocked = True
                        
                        # In your logs dashboard, you will see who submitted what key
                        # Perfect for checking your bank statement later
                        st.toast(f"UTR Submitted for verification: {clean_utr}") 
                        st.success("UTR Recorded! Opening Dashboard...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Transaction ID. Please enter the full 12-digit numerical UTR found in your UPI app receipt.")

else:
    # 3. This section unlocks ONLY after a valid 12-digit format is provided
    st.success("🔓 **Premium Active:** Visual Analysis Enabled")
    
    uploaded_file = st.file_uploader("Upload a photo of your joint or a medical report (PNG, JPG)", type=["png", "jpg", "jpeg"])
    
    def encode_image(upload):
        import base64
        return base64.b64encode(upload.getvalue()).decode('utf-8')

# 6. Handle User Input
if user_input := st.chat_input("Describe your pain or upload an image above..."):
    
    # Display user message and uploaded image
    with st.chat_message("user"):
        st.markdown(user_input)
        if uploaded_file:
            st.image(uploaded_file, width=250)

    # Prepare the message content for the AI
    message_content = [{"type": "text", "text": user_input}]
    
    # If a file is uploaded, attach it to the payload
    if uploaded_file is not None:
        base64_image = encode_image(uploaded_file)
        message_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        })

    # Save user's message to history
    st.session_state.messages.append({"role": "user", "content": message_content})

    # Generate Assistant Response
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                temperature=0.6,
            )
            ai_response = response.choices[0].message.content
            st.markdown(ai_response)
            
            # Save assistant's reply to history
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            st.error("Error communicating with the AI Engine.")
