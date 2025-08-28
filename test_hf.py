import streamlit as st
import google.generativeai as genai
from hfAPIkey import get_googlekey

# Load and configure Gemini API key
GEMINI_API_KEY = get_googlekey()
genai.configure(api_key=GEMINI_API_KEY)

# Pick Gemini model
MODEL_NAME = "gemini-1.5-flash"   # fast & affordable

# Streamlit setup
st.set_page_config(page_title="Medical Chatbot", page_icon="🩺", layout="wide")
st.title("🩺 Medical Chatbot")
st.caption("Disclaimer: This chatbot is not a substitute for professional medical advice. "
           "For emergencies, call your local emergency number immediately.")

# Sidebar with extra features
st.sidebar.title("⚙️ Features")
feature = st.sidebar.radio("Choose a feature:", [
    "General Chat", "Symptom Checker", "Drug Information", "First Aid", "Health Tips"
])

# Map each feature to its system instruction
feature_instructions = {
    "General Chat": "You are a helpful and safe medical assistant. Answer factually and concisely in 4-5 sentences.",
    "Symptom Checker": "You are a medical assistant. The user will describe symptoms. Suggest possible causes and advise seeing a doctor.",
    "Drug Information": "You are a medical assistant. Provide drug details (uses, dosage, side effects, precautions). Do NOT prescribe.",
    "First Aid": "You are a first-aid assistant. Give step-by-step safe first-aid instructions.",
    "Health Tips": "You are a health advisor. Provide preventive care tips (diet, lifestyle, exercise)."
}

# Initialize chat session if not already started
if "chat" not in st.session_state or "active_feature" not in st.session_state:
    st.session_state.active_feature = feature
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=feature_instructions[feature]
    )
    st.session_state.chat = model.start_chat(history=[])

# If user changes feature, reset with new system instruction but keep history
if feature != st.session_state.active_feature:
    st.session_state.active_feature = feature
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=feature_instructions[feature]
    )
    st.session_state.chat = model.start_chat(history=st.session_state.chat.history)

# Safety check function (emergency detection)
def check_emergency(text: str) -> bool:
    emergencies = ["chest pain", "can't breathe", "suicidal", "overdose", "severe bleeding"]
    return any(e in text.lower() for e in emergencies)

# Display previous chat history
for msg in st.session_state.chat.history:
    role = "assistant" if msg.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(msg.parts[0].text)

# Chat input
if user_input := st.chat_input("Ask me a medical question…"):
    # Emergency detection
    if check_emergency(user_input):
        st.chat_message("assistant").markdown(
            "🚨 This seems like a **medical emergency**. Please call your local emergency number immediately "
            "(e.g., 911/112) or visit the nearest hospital."
        )
    else:
        # Show user message
        st.chat_message("user").markdown(user_input)

        # Send only the user input (system prompt is hidden in model config)
        response = st.session_state.chat.send_message(user_input)

        # Show assistant reply
        with st.chat_message("assistant"):
            st.markdown(response.text)
