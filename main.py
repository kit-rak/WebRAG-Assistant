import os
import base64
import gc
import uuid
import requests
import math
from PIL import Image
from fpdf import FPDF
from dotenv import load_dotenv
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from colivara_py import ColiVara
from rag_code import Retriever, RAG
from firecrawl import FirecrawlApp
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Initialize session state
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.collection_name = f"webpage_collection{st.session_state.id}"
    st.session_state.file_cache = {}
    st.session_state.url_input = ""
    st.session_state.pdf_displayed = False
    st.session_state.language = "English"

session_id = st.session_state.id

# Helper Functions
def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def display_pdf(file):
    base64_pdf = base64.b64encode(file.read() if not isinstance(file, str) else open(file, "rb").read()).decode('utf-8')
    pdf_display = f"""<embed type="application/pdf" src="data:application/pdf;base64,{base64_pdf}" style="width: 100%; height: 800px;">"""
    st.markdown(pdf_display, unsafe_allow_html=True)

def create_pdf_from_screenshot(screenshot_url):
    response = requests.get(screenshot_url)
    response.raise_for_status()
    with open('image.png', 'wb') as f:
        f.write(response.content)
    image = Image.open('image.png')
    width, height = image.size
    slice_height = math.ceil(height / 10)
    pdf = FPDF(unit='pt', format=[width, slice_height])
    pdf.set_auto_page_break(auto=False)
    for i in range(10):
        top = i * slice_height
        bottom = min((i + 1) * slice_height, height)
        slice_img = image.crop((0, top, width, bottom))
        temp_filename = f'temp_slice_{i}.png'
        slice_img.save(temp_filename)
        pdf.add_page()
        pdf.image(temp_filename, x=0, y=0, w=width, h=bottom-top)
        os.remove(temp_filename)
    pdf_path = "screenshot_slices.pdf"
    pdf.output(pdf_path)
    return pdf_path

def deduplicate_lines(text):
    seen = set()
    result = []
    for line in text.split('\n'):
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            result.append(line)
    return '\n'.join(result)

# UI Styling
st.markdown("""
    <style>
        .main-title { font-size: 36px; font-weight: bold; color: #FF4B4B; }
        .subtitle { font-size: 18px; color: #ffffff; margin-bottom: 10px; }
        .summary-box {
            background-color: #222;
            color: #f0f0f0;
            padding: 15px;
            border-left: 5px solid #1f77b4;
            margin-bottom: 20px;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🔎 Multimodal RAG Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Powered by ColiVara, Firecrawl & Janus – Upload URLs, View PDFs, Ask Anything!</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 📄 Upload & Process Content")
    url_input = st.text_input("🌐 Webpage URL", value=st.session_state.url_input)
    st.session_state.url_input = url_input
    uploaded_file = st.file_uploader("📁 Or upload a PDF", type=["pdf"])
    st.session_state.language = st.selectbox("🌍 Preferred Language for Answers", ["English", "Spanish", "French", "German", "Chinese"])
    start_rag = st.button("🚀 Start Processing")

    if start_rag and (url_input or uploaded_file):
        try:
            with st.status("Processing content...", expanded=True) as status:
                if url_input:
                    if not is_valid_url(url_input):
                        st.warning("Please enter a valid URL (e.g., https://example.com)")
                        st.stop()
                    status.write("🔍 Scraping webpage with Firecrawl...")
                    try:
                        app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
                        scrape_result = app.scrape_url(url=url_input, formats=['screenshot@fullPage'], waitFor=10000)
                        if not scrape_result or not scrape_result.screenshot:
                            raise ValueError("No screenshot returned. The page may not be accessible.")
                    except Exception as e:
                        st.error(f"Firecrawl failed: {e}")
                        st.stop()
                    status.update(label="Creating PDF", state="running")
                    st.session_state.pdf_path = create_pdf_from_screenshot(scrape_result.screenshot)
                elif uploaded_file:
                    temp_path = f"uploaded_{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.read())
                    st.session_state.pdf_path = temp_path



                st.session_state.pdf_displayed = True
                file_key = f"{session_id}-webpage.pdf"
                if file_key not in st.session_state.file_cache:
                    status.update(label="Indexing content", state="running")
                    rag_client = ColiVara(api_key=os.getenv("COLIVARA_API_KEY"))
                    rag_client.create_collection(name=st.session_state.collection_name, metadata={"description": "Webpage/PDF content"})
                    rag_client.upsert_document(collection_name=st.session_state.collection_name, name="document", document_path=st.session_state.pdf_path)
                    retriever = Retriever(rag_client=rag_client, collection_name=st.session_state.collection_name)
                    st.session_state.query_engine = RAG(retriever=retriever)
                    st.session_state.file_cache[file_key] = st.session_state.query_engine
                else:
                    st.session_state.query_engine = st.session_state.file_cache[file_key]
                status.update(label="Processing complete!", state="complete")
            st.success("Ready to Chat!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    if st.session_state.get('pdf_displayed', False) and hasattr(st.session_state, 'pdf_path'):
        with st.expander("📘 View Extracted PDF", expanded=True):
            pdf_viewer(st.session_state.pdf_path)

# Clear button
st.button("Clear ↺", on_click=reset_chat)

# Chat History
if "messages" not in st.session_state:
    reset_chat()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"**{message['role'].capitalize()}:** {message['content']}")

# Chat Input
if prompt := st.chat_input("💬 Ask me anything about the webpage or PDF..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        language_prefix = f"Please respond in {st.session_state.language}. " if st.session_state.language != "English" else ""
        streaming_response = st.session_state.query_engine.query(language_prefix + prompt)
        for chunk in streaming_response:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        deduped = deduplicate_lines(full_response)
        message_placeholder.markdown(deduped)
    st.session_state.messages.append({"role": "assistant", "content": deduped})

# Auto Summary Option
if st.session_state.get("pdf_displayed", False) and hasattr(st.session_state, "query_engine"):
    with st.expander("🧠 Auto Summary"):
        if st.button("Generate Summary"):
            with st.spinner("Summarizing content..."):
                language_prefix = f"Please respond in {st.session_state.language}. " if st.session_state.language != "English" else ""
                summary_prompt = language_prefix + "Please provide a concise summary of the document."
                summary = st.session_state.query_engine.query(summary_prompt)
                st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
