# SpecForge | BRD-to-FSD Generator

SpecForge is an AI-powered BRD→FSD generator. It verifies BRD quality, runs feedback loops to fill gaps, and generates detailed Functional Specification Documents (FSDs) using Groq/OpenAI.

## 🚀 Features

- **Document Parsing**: Upload and parse BRDs in various formats, including PDF, DOCX, and raw text.
- **AI-Powered BRD Verification**: Before generating an FSD, the application uses an LLM (such as Groq) to analyze the provided BRD to ensure it contains sufficient detail, structure, and clarity.
- **Automated FSD Generation**: Generates a detailed Functional Specification Document based on the verified BRD using state-of-the-art LLMs (OpenAI, Groq).
- **Customizable Generation Settings**: Adjust the depth, terminology, language, and the target LLM provider through a dedicated Settings interface.
- **Export to Word**: Easily export the generated FSD directly to a Microsoft Word (`.docx`) file for easy sharing and further editing.
- **Modern UI (optional)**: Run a React UI backed by a FastAPI REST API.

## 🛠️ Technology Stack

- **Frontend/UI**: Streamlit (existing) or React (optional)
- **Backend/API**: FastAPI (optional, for React UI)
- **LLM Integrations**: 
  - [Groq](https://groq.com/) (Fast inference, reasoning)
  - OpenAI (Text generation)
- **Document Processing**: 
  - `PyMuPDF` for fast PDF parsing.
  - `python-docx` for reading and exporting Word documents.
- **Styling**: Custom CSS and Streamlit component styling.

## 📂 Project Structure

- `app.py`: The main entry point for the Streamlit application. Manages page routing and session state.
- `brd_core.py`: BRD verification + enrichment core logic (no UI).
- `brd_verifier_ui.py`: Streamlit renderer for verification results.
- `fsd_generator.py`: Module responsible for orchestrating the FSD generation using LLMs.
- `fsd_core.py`: FSD generation core logic (no UI).
- `file_parser.py`: Utility functions to extract text from uploaded PDF and DOCX files.
- `docx_exporter.py`: Handles exporting the generated FSD content to a structured `.docx` file.
- `llm_client.py`: Centralized client wrapper for making API calls to Groq and OpenAI.
- `prompt_engine.py`: Manages the prompt templates used for BRD verification and FSD generation tasks.
- `helpers.py`: Various helper functions used across the application.
- `api_server.py`: FastAPI backend exposing REST endpoints for a React UI.
- UI Pages:
  - `sidebar.py`: Application sidebar navigation.
  - `input_page.py`: File upload and BRD input interface.
  - `verify_page.py`: Interface displaying the BRD verification results.
  - `generation_page.py`: Controls and progress tracking for the FSD generation.
  - `output_page.py`: Displays the final FSD and provides download options.
  - `settings_page.py`: API key configuration and generation preferences.
- `main.css`: Custom stylesheet for the application UI.

## ⚙️ Installation

1. **Clone the repository** (or download the source files).
2. **Ensure you have Python 3.8+ installed.**
3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. **Set up API Keys**: You will need API keys from Groq and OpenAI. You can either set them in your environment variables or directly enter them in the application's **Settings** page.
2. **Run the Application**:

   ```bash
   ./venv/bin/streamlit run app.py
   ```

   Or run the modern React UI:

   Backend:
   ```bash
   ./venv/bin/uvicorn api_server:app --reload --port 8000
   ```

   Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Navigate through the App**:
   - **Input**: Upload your BRD or paste the text directly.
   - **Verify**: Review the AI's analysis of your BRD to ensure it's ready for FSD generation.
   - **Generation**: Trigger the FSD generation process.
   - **Output**: Review the generated specifications and download the `.docx` file.

## 🔒 Configuration

API keys and specific generation settings can be configured via the **Settings** page within the app. The application primarily supports the following environment variables (which can also be placed in a `.env` file):

- `GROQ_API_KEY`: Your Groq API key.
- `OPENAI_API_KEY`: Your OpenAI API key.

---
*Built with Streamlit/React and Generative AI.*
