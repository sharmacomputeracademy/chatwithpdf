import streamlit as st
import os
from main import PDFChatBot
import tempfile

# --- Page Config ---
st.set_page_config(
    page_title="PDF Intelligence Chat",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    .stSidebar {
        background-color: #111827;
        border-right: 1px solid #374151;
    }
    .chat-bubble {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        max-width: 80%;
    }
    .user-bubble {
        background-color: #2563eb;
        color: white;
        align-self: flex-end;
    }
    .bot-bubble {
        background-color: #334155;
        color: #f8fafc;
        border: 1px solid #475569;
    }
    h1, h2, h3 {
        color: #60a5fa !important;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "bot" not in st.session_state:
    st.session_state.bot = PDFChatBot()

if "processed" not in st.session_state:
    st.session_state.processed = False

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    
    if uploaded_file is not None and not st.session_state.processed:
        with st.spinner("Processing PDF... Creating Brain... 🧠"):
            # Save uploaded file to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                pages, chunks = st.session_state.bot.ingest_pdf(tmp_path)
                st.success(f"✅ Loaded {pages} pages and {chunks} chunks!")
                st.session_state.processed = True
                os.remove(tmp_path) # Clean up
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    if st.button("Clear Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()

    st.info("This AI assistant answers questions based only on the content of the uploaded PDF.")

# --- Main Interface ---
st.title("📄 PDF Intelligence Assistant")
st.markdown("##### *Chat with your documents using RAG technology*")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask something about the document..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot response
    with st.chat_message("assistant"):
        if not st.session_state.processed:
            response = "⚠️ Please upload a PDF in the sidebar first!"
            st.warning(response)
        else:
            with st.spinner("Analyzing context..."):
                response = st.session_state.bot.ask(prompt)
                st.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})
