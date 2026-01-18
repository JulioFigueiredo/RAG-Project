import streamlit as st
import requests

st.title("🤖 Chat with Your Data (RAG)")

uploaded_file = st.file_uploader("Envie seu PDF", type="pdf")

if uploaded_file:
    files = {"file": uploaded_file.getvalue()}
    response = requests.post("http://localhost:8000/upload", files=files)
    if response.status_code == 200:
        st.success("PDF processado e vetorizado com sucesso!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Pergunte algo sobre o documento..."):
    # Question
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Request to FastAPI
    with st.spinner("A IA está pensando..."):
        api_response = requests.post(
            "http://localhost:8000/chat", 
            json={"question": prompt}
        )
        answer = api_response.json().get("answer")

    # API Response
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})