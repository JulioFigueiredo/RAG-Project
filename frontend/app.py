import streamlit as st
import requests
import os

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")
st.title("🤖 Chat with Your Data (RAG)")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file:
    if "last_file_name" not in st.session_state or st.session_state.last_file_name != uploaded_file.name:
        
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        
        with st.spinner("Processing PDF automatically..."):
            try:
                response = requests.post(f"{BACKEND_URL}/upload", files=files)
                
                if response.status_code == 200:
                    st.success("✅ PDF processed and vectorized successfully!")
                    st.session_state.last_file_name = uploaded_file.name
                else:
                    st.error(f"Backend Error: {response.text}")
                    
            except Exception as e:
                st.error(f"Connection Error: {e}")

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