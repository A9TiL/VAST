import streamlit as st
import requests
import time
import os
import urllib.parse
import random


st.set_page_config(page_title="VAST Engine | NotebookLM", page_icon="🧠", layout="wide")

API_URL = "https://vast-engine-backend.onrender.com/api/v1"
ROOT_URL = "https://vast-engine-backend.onrender.com"


if "backend_active" not in st.session_state:
    st.session_state.backend_active = False

def check_backend_status():
    """Fires a single ping to the root URL. A 404 means FastAPI is awake!"""
    try:
        res = requests.get(ROOT_URL, timeout=3)

        if res.status_code == 404: 
            return True
    except requests.exceptions.RequestException:
        pass
    return False


if not st.session_state.backend_active:
    is_live = check_backend_status()
    
    if is_live:

        st.session_state.backend_active = True
        st.rerun() 
    else:
       
        st.markdown("## 🧠 VAST Engine is currently offline.")
        st.warning("The cloud server is sleeping to save resources. Please hold on while we spin it up!")
        st.markdown("This page will automatically refresh every 5 seconds until the backend goes live.")
        
        st.write("")
        
       
        st.markdown(
            f'<a href="{ROOT_URL}" target="_blank" style="'
            f'text-decoration: none; padding: 0.5rem 1rem; border-radius: 0.5rem; '
            f'background-color: #FF4B4B; color: white; font-weight: bold; display: inline-block;'
            f'">🚀 Manually Trigger Backend</a>', 
            unsafe_allow_html=True
        )
        st.markdown("*Note: Clicking this will open a new tab. Once it says 'Not Found', you can close it and return here.*")
        
        st.write("")
        

        with st.spinner("Waiting for backend container to boot..."):
            time.sleep(5) 
            st.rerun()    
            

        st.stop()



st.title("🧠 VAST Engine")
st.markdown("Your Local, Retrieval-Augmented Generation System.")
st.success("🟢 System Online & Database Connected")

with st.sidebar:
    st.header("⚙️ Engine Configuration")
    
    user_api_key = st.text_input(
        "Groq API Key", 
        type="password", 
        help="Required for the LLM to generate answers. Get a free key at console.groq.com."
    )
    
    st.info(
        "**🔒 Privacy & Storage:**\n"
        "- Files are processed in a secure, isolated container.\n"
        "- Your API key is used strictly in-memory and never saved.\n"
        "- The vault searches only the documents you explicitly upload."
    )
    st.divider()
    
    st.header("📥 Ingestion Engine")
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "md", "txt"])
    
    if uploaded_file and st.button("📤 Send to Server", use_container_width=True):
        with st.spinner(f"Uploading {uploaded_file.name}..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                res = requests.post(f"{API_URL}/upload", files=files)
                if res.status_code == 200:
                    st.success("File landed in the vault!")
                else:
                    st.error(f"Upload rejected. Server responded with status: {res.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    if st.button("🔄 Re-Index Knowledge Vault", use_container_width=True, type="primary"):
        with st.spinner("Chunking & Embedding..."):
            try:
                requests.post(f"{API_URL}/index")
                st.success("Vault Updated!")
            except Exception as e:
                st.error("Indexing failed.")

tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "🔍 Raw Vector Search", "📊 System Dashboard"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your documents..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    res = requests.post(f"{API_URL}/ask", json={"query": prompt}).json()
                    answer = res.get("answer", "Error.")
                    st.markdown(answer)
                    st.caption(f"⏱️ {res.get('execution_time_ms', 0):.2f} ms | 📚 {', '.join(res.get('sources', []))}")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error("API Error")

with tab2:
    st.subheader("Query the Vector Database")
    st.markdown("Bypass the LLM and see exactly which chunks match your query.")
    
    search_query = st.text_input("Enter search keywords...")
    k_value = st.slider("Retrieval depth (top_k)", min_value=1, max_value=20, value=3, step=1)
    
    if st.button("Search Vault"):
        if search_query:
            with st.spinner("Searching..."):
                try:
                    payload = {
                        "query": search_query, 
                        "top_k": k_value
                    }
                    res = requests.post(f"{API_URL}/search", json=payload)
                    
                    if res.status_code == 200:
                        data = res.json()
                        results = data.get("results", [])
                        exec_time = data.get("execution_time_ms", 0)
                        
                        if results:
                            st.success(f"Found {len(results)} matches in {exec_time:.2f} ms")
                            for i, match in enumerate(results):
                                metadata = match.get('metadata', {})
                                source = metadata.get('source_file', 'Unknown')
                                distance = match.get('distance', 0.0)
                                
                                with st.expander(f"Match {i+1} | Source: {source}"):
                                    st.write(match.get('text', 'No text found.'))
                                    st.caption(f"Relevance Score (Distance): {distance:.4f}")
                                    with st.popover("View Raw Metadata"):
                                        st.json(metadata)
                        else:
                            st.info("No relevant documents found.")
                    else:
                        st.error(f"Search failed: {res.text}")
                except Exception as e:
                    st.error(f"Search endpoint error: {e}")

with tab3:
    st.subheader("Database Analytics")
    if st.button("Fetch Real-Time Stats"):
        with st.spinner("Querying ChromaDB..."):
            try:
                stats = requests.get(f"{API_URL}/stats").json()
                st.metric(label="Total Semantic Chunks", value=stats.get("total_chunks", 0))
                
                st.markdown("### Indexed Files")
                for file in stats.get("indexed_files", []):
                    with st.expander(f"📄 {file}"):
                        file_name = urllib.parse.quote(file)
                        
                        
                        file_url = f"{API_URL}/view/{file_name}"
                        
                        st.markdown(f"**Action:** [🔗 Click here to open/download {file}]({file_url})")
                        st.caption("PDFs will open in a new tab. Other files will download.")
            except Exception as e:
                st.error("Failed to load stats.")