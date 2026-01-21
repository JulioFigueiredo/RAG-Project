import streamlit as st
import requests
import os

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")
st.title("🤖 Chat with Your Data (RAG)")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MAX_FILE_SIZE_MB = 20

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ File too large! ({file_size_mb:.1f}MB) Maximum: {MAX_FILE_SIZE_MB}MB")
    elif "last_file_name" not in st.session_state or st.session_state.last_file_name != uploaded_file.name:
        st.info(f"📄 File: {uploaded_file.name} ({file_size_mb:.1f}MB)")
        
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        
        with st.spinner("Processing PDF automatically..."):
            try:
                response = requests.post(f"{BACKEND_URL}/upload", files=files)
                
                if response.status_code == 200:
                    st.success("✅ PDF processed and vectorized successfully!")
                    st.session_state.last_file_name = uploaded_file.name
                else:
                    error_msg = response.json().get("detail", response.text)
                    st.error(f"❌ Backend Error: {error_msg}")
                    
            except Exception as e:
                st.error(f"❌ Connection Error: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask something about the document..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API
    with st.spinner("AI is thinking..."):
        try:
            payload = {"question": prompt}
            api_response = requests.post(f"{BACKEND_URL}/chat", json=payload)
            
            if api_response.status_code == 200:
                data = api_response.json()
                answer = data.get("answer", "Error: No answer key found in response.")
            else:
                answer = f"API Error: {api_response.text}"
                
        except Exception as e:
            answer = f"Connection Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})