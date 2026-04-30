import streamlit as st
from main import PDFChatBot
import os
import tempfile

# Basic Page Setup
st.set_page_config(page_title="Simple PDF Chat", layout="wide")

st.title("📄 Simple PDF Chat")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = PDFChatBot()

if "ready" not in st.session_state:
    st.session_state.ready = False

# --- Sidebar for PDF Upload ---
with st.sidebar:
    st.header("PDF Upload")
    uploaded_file = st.file_uploader("Upload your document", type="pdf")
    
    if uploaded_file and not st.session_state.ready:
        with st.spinner("Processing..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                pages, chunks = st.session_state.chatbot.ingest_pdf(tmp_path)
                st.success(f"Loaded {pages} pages.")
                st.session_state.ready = True
                os.remove(tmp_path)
            except Exception as e:
                st.error(f"Error: {e}")
    
    if st.button("Clear History"):
        st.session_state.messages = []
        st.rerun()

# --- Main Frame: Chat Interface ---
# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about your document..."):
    if not st.session_state.ready:
        st.warning("Please upload a PDF in the sidebar first.")
    else:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                answer = st.session_state.chatbot.ask(prompt)
                st.markdown(answer)
        
        st.session_state.messages.append({"role": "assistant", "content": answer})
