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
# Make sure "Achala_DV_1.png" is in the same directory as this script
logo = Image.open("Achala_Digital_Vaidya.png")

# 2. Update the page configuration to use the image as the browser tab icon
st.set_page_config(
    page_title="Achala Digital Vaidya: Kitchen Pharmacy AI", 
    page_icon=logo, 
    layout="centered"
)

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

# 6. Handle User Input
if user_input := st.chat_input("Describe your pain or symptoms (e.g., severe knee pain, morning stiffness)..."):
    
    # Display user's message in the UI
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Save user's message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate Assistant Response
    with st.chat_message("assistant"):
        try:
            # We use gpt-4o-mini as it is fast, highly accurate, and incredibly affordable
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
            st.info("Please make sure your API key is correctly initialized.")
