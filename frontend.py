import streamlit as st
import requests 
import time

st.set_page_config(
    page_title="VAST Engine",
    page_icon="🧠",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/api/v1"

st.title("🧠 VAST Engine")
st.markdown("Yout Local, Retrieval-Augmentated Generation System.")

with st.sidebar:
    st.header("⚙️ Engine controls")
    
    if st.button("🔄 Re-Index Knowledge Vault" , use_container_width=True):
        with st.spinner("Chunking and Embedding documents..."):
            try:
                res = requests.post(f"{API_URL}/index")
                if res.status_code==200:
                    st.success("Vault successfully updated.")
                else:
                    st.error("Failed to index documents.")
            except Exception as e :
                st.error(f"API Error : {e}")
    st.divider()
    st.subheader("📊 Vault Statistics")
    try:
        stats = requests.get(f"{API_URL}/stats").json()
        st.metric(label="Total Semantic Chunks", value=stats.get("total_chunks", 0))
        st.write("**Indexed Files:**")
        for file in stats.get("indexed_files", []):
            st.caption(f"📄 {file}")
    except:
        st.warning("Backend API is currently offline.")
        
st.subheader("Chat with your Documents")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
if prompt := st.chat_input("Ask a question about your documents..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Searching the vault..."):
            try:
                
                response = requests.post(f"{API_URL}/ask", json={"query": prompt})
                data = response.json()
                
                answer = data.get("answer", "Error: No answer returned.")
                sources = data.get("sources", [])
                latency = data.get("execution_time_ms", 0)
                
                st.markdown(answer)
                
                st.caption(f"⏱️ **Latency:** {latency:.2f} ms | 📚 **Sources:** {', '.join(sources)}")
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Failed to connect to the VAST API: {e}")