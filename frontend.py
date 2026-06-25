import streamlit as st
import requests
import time
import os
import urllib.parse


st.set_page_config(page_title="VAST Engine | NotebookLM", page_icon="🧠", layout="wide")
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")


def check_health():
    try:
        res = requests.get(f"{API_URL.replace('/api/v1', '')}/health")
        return res.status_code == 200
    except:
        return False


st.title("🧠 VAST Engine")
st.markdown("Your Local, Retrieval-Augmented Generation System.")

if check_health():
    st.success("🟢 System Online & Database Connected")
else:
    st.error("🔴 System Offline - Check Backend Container")


with st.sidebar:
    
    st.header("⚙️ Engine Configuration")
    
    # The API Key Input
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
                    st.error("Upload rejected.")
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
                    st.error(f"Search endpoint not configured or offline: {e}")


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
                        
                        file_url = f"http://localhost:8000/api/v1/view/{file_name}"
                        
                        st.markdown(f"**Action:** [🔗 Click here to open/download {file}]({file_url})")
                        st.caption("PDFs will open in a new tab. Other files will download.")
            except Exception as e:
                st.error("Failed to load stats.")