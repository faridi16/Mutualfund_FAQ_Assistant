import streamlit as st
import chat
import uuid

# Initialize Streamlit Page Config
st.set_page_config(page_title="HDFC Mutual Fund FAQ", page_icon="📈", layout="wide")

# Custom Premium CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    /* Dark Premium Theme Overrides */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header Gradient */
    .gradient-text {
        background: linear-gradient(90deg, #ef4444, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
    }
    
    /* Glassmorphism Chat Bubbles */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    .stChatMessage:hover {
        transform: translateY(-2px);
    }
    
    /* User Message distinct style */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    /* Buttons with micro-animations */
    .stButton>button {
        background: rgba(239, 68, 68, 0.1);
        color: #f87171;
        border-radius: 8px;
        border: 1px solid rgba(239, 68, 68, 0.3);
        width: 100%;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: rgba(239, 68, 68, 0.2);
        border-color: rgba(239, 68, 68, 0.6);
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
        transform: scale(1.02);
    }
    
    /* Primary action button (New Chat) */
    .primary-btn>div>button {
        background: linear-gradient(90deg, #ef4444, #dc2626);
        color: white;
        border: none;
    }
    .primary-btn>div>button:hover {
        background: linear-gradient(90deg, #dc2626, #b91c1c);
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
    }
    
    /* Sidebar Chat List Buttons (looks like links) */
    .chat-list-btn>div>button {
        background: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 5px !important;
        box-shadow: none !important;
    }
    .chat-list-btn>div>button:hover {
        color: #e2e8f0 !important;
        transform: translateX(5px) !important;
    }
    
    /* Disclaimer */
    .disclaimer {
        font-size: 0.85em;
        color: #64748b;
        text-align: center;
        padding: 15px;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Cache Model Initialization
@st.cache_resource(show_spinner="Loading Models (Llama 3.3 70b) and Vector DB...")
def load_models():
    return chat.init_models()

try:
    llm, vectorstore = load_models()
except SystemExit:
    st.error("⚠️ GROQ_API_KEY environment variable is not set in `.env`.")
    st.stop()

# --- Multi-Chat Session Management ---
if "chats" not in st.session_state:
    # Initialize with one default chat
    default_id = str(uuid.uuid4())
    st.session_state.chats = {default_id: {"title": "New Chat", "messages": []}}
    st.session_state.current_chat_id = default_id

# Helper to create a new chat
def create_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

# --- Sidebar UI ---
with st.sidebar:
    st.markdown("<h2 class='gradient-text'>HDFC Assistant</h2>", unsafe_allow_html=True)
    
    # New Chat Button
    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
    if st.button("➕ New Chat"):
        create_new_chat()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Historical Chats List
    st.markdown("### Recent Chats")
    for chat_id, chat_data in reversed(st.session_state.chats.items()):
        # Highlight active chat
        prefix = "💬 " if chat_id == st.session_state.current_chat_id else "⚪ "
        
        st.markdown("<div class='chat-list-btn'>", unsafe_allow_html=True)
        if st.button(f"{prefix} {chat_data['title'][:20]}...", key=chat_id):
            st.session_state.current_chat_id = chat_id
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.divider()
    st.markdown("""
    ### Quick Queries
    *Clicking will ask in the current chat.*
    """)
    if st.button("What is the exit load for HDFC Large Caps?"):
        st.session_state.preset_query = "What is the exit load for HDFC Large Caps?"
    if st.button("What is the NAV of HDFC Gold ETF?"):
        st.session_state.preset_query = "What is the NAV of HDFC Gold ETF?"
    if st.button("Should I invest in HDFC Mid Cap?"):
        st.session_state.preset_query = "Should I invest in HDFC Mid Cap?"

# --- Main Chat UI ---
# App Header
st.markdown("<h1 class='gradient-text'>📈 Mutual Fund FAQ</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #fbbf24; font-weight: bold;'>⚠️ Facts-only. No investment advice.</p>", unsafe_allow_html=True)

# Get current chat messages
current_chat = st.session_state.chats[st.session_state.current_chat_id]

# Display Chat History
for message in current_chat["messages"]:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Check for Preset Query from Sidebar
preset = st.session_state.pop("preset_query", None)

# Chat Input Trigger
if prompt := st.chat_input("Ask about HDFC Mutual Funds..."):
    preset = prompt

# Process Input
if preset:
    # Update title of chat if it's the first message
    if current_chat["title"] == "New Chat":
        current_chat["title"] = preset
        
    # Display User Message
    with st.chat_message("user", avatar="👤"):
        st.markdown(preset)
    current_chat["messages"].append({"role": "user", "content": preset})

    # Generate Assistant Response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing semantics and searching database..."):
            answer = chat.process_query(llm, vectorstore, preset)
            st.markdown(answer)
    
    current_chat["messages"].append({"role": "assistant", "content": answer})
    
    # Rerun to update sidebar title if it was the first message
    if len(current_chat["messages"]) <= 2:
        st.rerun()

st.markdown("<div class='disclaimer'>Information provided is for educational purposes only. Past performance is not indicative of future returns.</div>", unsafe_allow_html=True)
