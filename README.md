# 🔎 Multimodal RAG Assistant

A Streamlit-based application that enables users to query and summarize **PDFs** and **webpages** using a multimodal Retrieval-Augmented Generation (RAG) pipeline. It integrates visual and text understanding powered by **ColiVara**, **Firecrawl**, and **Janus**.

## ✨ Features

* 🌐 Scrape and analyze webpages via Firecrawl.
* 📄 Upload PDFs for intelligent processing.
* 🤖 Ask questions and receive answers based on document visuals and content.
* 🧠 Automatic summarization of documents.
* 🌍 Multilingual support (English, Spanish, French, German, Chinese).

## 🧱 Tech Stack

* **Streamlit** – Interactive UI
* **Firecrawl** – Web scraping and screenshots
* **ColiVara** – Vector search and document indexing
* **Janus** – Multimodal vision-language transformer
* **FPDF** – PDF generation
* **Pillow (PIL)** – Image processing

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/kit-rak/WebRAG-Assistant.git
cd WebRAG-Assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Environment Variables

Create a `.env` file in the root directory:

```env
FIRECRAWL_API_KEY=your_firecrawl_api_key
COLIVARA_API_KEY=your_colivara_api_key
```

### 4. Launch the App

```bash
streamlit run main.py
```
## 🧠 Installing DeepSeek Janus
To integrate the Janus multimodal model into your project, follow these steps:

### 1. Clone the Janus Repository

```bash
git clone https://github.com/deepseek-ai/Janus.git
cd Janus
```

### 2. Install Dependencies

```bash
pip install -e .
```

This command installs the Janus package in editable mode, allowing for easy development and updates.

### 3. (Optional) Install Gradio for Demo Interface
If you wish to explore the demo interface provided by Janus:

```bash
pip install -e .[gradio]
```

### 4. Launch the Janus Demo App
To run the demo application:

```bash
python demo/app_januspro.py
```

Access the application at http://localhost:7860.

Note: Ensure that your system meets the necessary requirements for running DeepSeek Janus efficiently. For optimal performance, a CUDA-capable GPU is recommended.

## 🧠 How It Works

1. **Input**: User submits a URL or PDF file.
2. **Firecrawl** (for URLs): Takes a full-page screenshot and returns it.
3. **PDF Generation**: Screenshot is sliced and converted into a PDF.
4. **Indexing**: Content is indexed using ColiVara's vector database.
5. **Querying**: Janus LLM receives the visual context and responds intelligently.
6. **Chat**: Users interact via chat or generate summaries.

## 🗀 Interface Preview

Here’s how the app looks in action:

![App Screenshot](/assets/WebRAG.png)

## 📁 Project Structure

```
├── main.py            # Streamlit app UI
├── rag_code.py        # RAG + Janus integration logic
├── requirements.txt   # Python dependencies
└── .env               # Environment variable file (not committed)
```

## 📌 Notes

* Ensure that GPU support is available for Janus LLM inference.
* Image-rich documents yield the best results with this multimodal approach.
* PDFs are visually parsed – not just based on raw text.

## 📜 License

This project is licensed under the MIT License.

## 📬 Contact
- **LinkedIn:** [kit-rak](https://www.linkedin.com/in/kit-rak)
- **GitHub:** [kit-rak](https://github.com/kit-rak)

🚀 **Happy Analyzing!**
