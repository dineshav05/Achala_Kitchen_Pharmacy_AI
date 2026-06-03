import streamlit as st
from PIL import Image
from openai import OpenAI
import base64
import hashlib
import markdown

# 1. Initialize the OpenAI Client Safely
# This tells the code to look for the key in Streamlit's secure dashboard, NOT in the code.
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("API Key not found. Please set it up in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# --- 2. UI Configuration ---

# 1. Load your custom logo image FIRST
# Make sure "Achala_Digital_Vaidya.png" is in the same directory as this script
logo = Image.open("Achala_Digital_Vaidya.png")

# 2. Update the page configuration to use the image as the browser tab icon
st.set_page_config(
    page_title="Achala Digital Vaidya: Kitchen Pharmacy AI", 
    page_icon=logo, 
    layout="centered"
)

# 3. Function to securely encode your logo for the web UI
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# 4. Create the base64 string (THIS IS THE LINE THAT WAS MISSING!)
logo_base64 = get_base64_image("Achala_Digital_Vaidya.png")

# 5. The Responsive HTML/CSS Header
# This Flexbox design forces the logo and text to stay perfectly centered on all screen sizes
responsive_header = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 10px;">
        <img src="data:image/png;base64,{logo_base64}" width="90" style="margin-bottom: 15px;">
         <div class="flex items-center justify-between p-4 bg-white shadow-sm">
          <h1 class="text-base font-bold text-slate-900">
            Achala <span class="font-light text-slate-500">Vaidya</span>
          </h1>
          
          <div class="px-2.5 py-1 bg-amber-50 rounded-full border border-amber-200/60">
            <p class="text-xs font-medium text-amber-800">
              🍳 Kitchen Pharmacy <span class="text-[10px] bg-amber-700 text-white px-1 py-0.2 rounded ml-0.5">AI</span>
            </p>
          </div>
        </div>
        <p style="color: #888888; font-size: 0.95rem; margin-top: 10px; margin-bottom: 20px;">
            "Decode your diagnosis. Heal with heritage. An empowering Ayurvedic guide to joint and back pain, inspired by Shri Rajiv Dixit Ji."
        </p>
    </div>
   
    <hr style="margin-bottom: 30px;">
"""

# Inject the custom responsive header into the app
st.markdown(responsive_header, unsafe_allow_html=True)

# --- Sidebar Settings ---
with st.sidebar:
    st.title("⚙️ Preferences")
    selected_language = st.selectbox(
        "🌐 Choose Report Language:",
        ["English", "Hindi (हिंदी)", "Kannada (ಕನ್ನಡ)", "Tamil (தமிழ்)", "Telugu (తెలుగు)", "Marathi (मराठी)", "Gujarati (ગુજરાતી)", "Bengali (বাংলা)"]
    )
    st.info(f"The Digital Vaidya will automatically analyze your reports and reply in **{selected_language}**.")

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

# --- Render Chat History ---
for message in st.session_state.messages:
    
    # 🚨 THE FIX: Skip drawing the system prompt on the screen!
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        
        # 1. If it's a normal string (like the AI's response or a normal text chat)
        if isinstance(message["content"], str):
            st.markdown(message["content"])
            
        # 2. If it is a complex payload list (like when the user uploads an image)
        elif isinstance(message["content"], list):
            for item in message["content"]:
                # Only print the text portion of the payload to the screen
                if item["type"] == "text":
                    st.markdown(item["text"])
                # We hide the massive base64 image string and just show a neat little tag
                elif item["type"] == "image_url":
                    st.caption("📎 *Image/Report Attached*")

# 1. Initialize a memory bank for processed files
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

# 1. Initialize states for payment tracking
if "premium_unlocked" not in st.session_state:
    st.session_state.premium_unlocked = False #True for no validate
if "show_qr" not in st.session_state:
    st.session_state.show_qr = False #True for no validate

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
    # This section unlocks ONLY after a successful payment
    st.success("🔓 **Premium Active:** Visual Analysis Enabled")
    
   # 2. The File Uploader
    uploaded_file = st.file_uploader("Upload a photo of your joint or a medical report (PNG, JPG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        import hashlib
        file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
        
        # Initialize memory for analyzed files if it doesn't exist
        if "analyzed_files" not in st.session_state:
            st.session_state.analyzed_files = []
            
        # Check if this exact file has already been processed by the AI
        if file_hash in st.session_state.analyzed_files:
            st.warning("⚠️ Kindly upload a report or image only once. This is a duplicate.")
        else:
            st.success("✅ Image loaded successfully! Please type your symptoms in the chat box below and hit Send to begin.")
            
    def encode_image(upload):
        import base64
        return base64.b64encode(upload.getvalue()).decode('utf-8')


# Place this function near the top of your file with your other functions
def display_letterhead_report(ai_content, logo_base64_string):
    """Wraps the AI text in a beautiful Achala Enterprises digital letterhead."""
    
    # Notice how the HTML touches the absolute left edge. No spaces!
    letterhead_html = f"""
<div style="border: 2px solid #0f4c5c; border-radius: 8px; padding: 25px; background-color: #ffffff; color: #2b2b2b; font-family: 'Arial', sans-serif; box-shadow: 0px 4px 15px rgba(0,0,0,0.05); margin-top: 20px;">
    <div style="display: flex; align-items: center; border-bottom: 2px solid #0f4c5c; padding-bottom: 15px; margin-bottom: 25px;">
        <img src="data:image/png;base64,{logo_base64_string}" width="70" style="margin-right: 20px;">
        <div>
            <h2 style="margin: 0; color: #0f4c5c; font-size: 1.6rem; letter-spacing: 1px;">Achala Enterprises</h2>
            <p style="margin: 0; font-size: 0.95rem; color: #666666; font-weight: bold;">Digital Vaidya • Advanced Visual Analysis Report</p>
        </div>
    </div>
    <div style="line-height: 1.7; font-size: 1.05rem;">
        {ai_content}
    </div>
    <div style="border-top: 1px solid #e0e0e0; margin-top: 30px; padding-top: 15px; text-align: center; font-size: 0.85rem; color: #888888;">
        <p style="margin: 0; font-weight: bold;">Guided by the Ayurvedic principles of Shri Rajiv Dixit Ji.</p>
        <p style="margin: 5px 0 0 0;"><i>Disclaimer: This report is generated by AI for educational purposes and holistic wellness. Always consult a qualified medical professional before altering prescribed treatments.</i></p>
    </div>
</div>
"""
    
    st.markdown(letterhead_html, unsafe_allow_html=True)

# 6. Handle User Input
# --- The Chat Input and AI Execution Block ---
if user_input := st.chat_input("Describe your pain or upload an image above..."):
    
    # 1. Display user message and uploaded image
    with st.chat_message("user"):
        st.markdown(user_input)
        if uploaded_file:
            st.image(uploaded_file, width=250)

    # 2. Prepare the message content for the AI
    message_content = [{"type": "text", "text": user_input}]
    
    if uploaded_file is not None:
        import hashlib
        current_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
        
        # SMART CACHE: Only attach the image to the AI payload if it's brand new
        if current_hash not in st.session_state.analyzed_files:
            base64_image = encode_image(uploaded_file)
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
            # Add to our memory bank so it triggers the duplicate warning next time
            st.session_state.analyzed_files.append(current_hash)

    # Save user's message to history
    st.session_state.messages.append({"role": "user", "content": message_content})

    # 3. Generate Assistant Response
    with st.chat_message("assistant"):
        try: # --- OUTER TRY BLOCK BEGINS ---
            
            # --- SMART TRANSLATION PAYLOAD ---
            # Create a temporary copy of the chat history
            api_messages = st.session_state.messages.copy()
            
            # Inject a strict system command telling the AI to use the user's selected language
            api_messages.append({
                "role": "system", 
                "content": f"CRITICAL TRANSLATION RULE: You MUST generate your ENTIRE response, including the report analysis, headings, and Ayurvedic recommendations, strictly in {selected_language}. Ensure medical terms are translated beautifully so the common man can understand."
            })
            
            # Call the AI Engine using the modified payload
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=api_messages,
                temperature=0.6,
            )
            ai_response = response.choices[0].message.content
            
            # --- THE CONDITIONAL RENDERING BLOCK ---
            if uploaded_file is not None:
                # 1. Display the premium letterhead in the UI
                fresh_logo_base64 = get_base64_image("Achala_Digital_Vaidya.png")
                display_letterhead_report(ai_response, fresh_logo_base64)
                
                # 2. Build the printable HTML version
                # First, translate the AI's Markdown into beautifully structured HTML
                structured_html_content = markdown.markdown(ai_response, extensions=['extra', 'sane_lists', 'nl2br'])
                # Now, inject it into a professionally styled medical template
                report_html = f"""
                <html>
                <head>
                    <meta charset="utf-8">
                    <style>
                        /* Professional Medical Report CSS Styling */
                        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #2b2b2b; background-color: #f4f7f6; padding: 40px; }}
                        .report-container {{ max-width: 800px; margin: 0 auto; background-color: #ffffff; padding: 50px; border-top: 8px solid #0f4c5c; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-radius: 8px; }}
                        .header-section {{ display: flex; align-items: center; border-bottom: 2px solid #e0e0e0; padding-bottom: 20px; margin-bottom: 30px; }}
                        .header-text h2 {{ margin: 0; color: #0f4c5c; font-size: 28px; letter-spacing: 0.5px; }}
                        .header-text p {{ margin: 5px 0 0 0; color: #666; font-weight: bold; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
                        
                        /* Translating AI Markdown elements into clean medical formatting */
                        .content-section {{ line-height: 1.8; font-size: 15px; color: #333; }}
                        .content-section h3 {{ color: #0f4c5c; border-bottom: 1px solid #f0f0f0; padding-bottom: 8px; margin-top: 35px; font-size: 20px; }}
                        .content-section ul {{ padding-left: 20px; margin-bottom: 20px; }}
                        .content-section li {{ margin-bottom: 10px; }}
                        .content-section strong {{ color: #1a1a1a; }}
                        
                        .footer-section {{ margin-top: 50px; border-top: 1px solid #e0e0e0; padding-top: 20px; font-size: 12px; color: #888; text-align: center; line-height: 1.5; }}
                    </style>
                </head>
                <body>
                    <div class="report-container">
                        <div class="header-section">
                            <img src="data:image/png;base64,{fresh_logo_base64}" width="80" style="margin-right: 25px;">
                            <div class="header-text">
                                <h2>Achala Enterprises</h2>
                                <p>Digital Vaidya • Advanced Visual Analysis</p>
                            </div>
                        </div>
                        
                        <div class="content-section">
                            {structured_html_content}
                        </div>
                        
                        <div class="footer-section">
                            <b>Guided by the Ayurvedic principles of Shri Rajiv Dixit Ji.</b><br><br>
                            <i>Disclaimer: This report is generated by AI for educational purposes and holistic wellness.<br>
                            Always consult a qualified medical professional before altering prescribed treatments.</i>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # 3. Native Download Button 
                st.download_button(
                    label="📥 Download Medical Report",
                    data=report_html,
                    file_name="Achala_Digital_Vaidya_Report.html",
                    mime="text/html",
                    type="primary"
                )
                    
            else:
                # If it is a normal text chat, render normal chat text
                st.markdown(ai_response)
            
            # Save assistant's reply to history
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e: # --- THIS IS THE RESTORED EXCEPT BLOCK! ---
            st.error("Error communicating with the AI Engine. Please check your API key.")
