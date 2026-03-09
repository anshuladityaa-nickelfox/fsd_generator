# SpecForge | BRD-to-FSD Generator

SpecForge is an AI-powered Streamlit application designed to automatically convert Business Requirement Documents (BRDs) into structured, comprehensive Functional Specification Documents (FSDs). It leverages the power of advanced Large Language Models (like Groq and Gemini) to verify business requirements and generate technical specifications.

## 🚀 Features

- **Document Parsing**: Upload and parse BRDs in various formats, including PDF, DOCX, and raw text.
- **AI-Powered BRD Verification**: Before generating an FSD, the application uses an LLM (such as Groq) to analyze the provided BRD to ensure it contains sufficient detail, structure, and clarity.
- **Automated FSD Generation**: Generates a detailed Functional Specification Document based on the verified BRD using state-of-the-art LLMs (Gemini, Groq).
- **Customizable Generation Settings**: Adjust the depth, terminology, language, and the target LLM provider through a dedicated Settings interface.
- **Export to Word**: Easily export the generated FSD directly to a Microsoft Word (`.docx`) file for easy sharing and further editing.

## 🛠️ Technology Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **LLM Integrations**: 
  - [Groq](https://groq.com/) (Fast inference, reasoning)
  - [Google Gemini](https://deepmind.google/technologies/gemini/) (Contextual generation)
- **Document Processing**: 
  - `PyMuPDF` for fast PDF parsing.
  - `python-docx` for reading and exporting Word documents.
- **Styling**: Custom CSS and Streamlit component styling.

## 📂 Project Structure

- `app.py`: The main entry point for the Streamlit application. Manages page routing and session state.
- `brd_verifier.py`: Contains the logic for analyzing and verifying the quality of the uploaded BRD.
- `fsd_generator.py`: Module responsible for orchestrating the FSD generation using LLMs.
- `file_parser.py`: Utility functions to extract text from uploaded PDF and DOCX files.
- `docx_exporter.py`: Handles exporting the generated FSD content to a structured `.docx` file.
- `llm_client.py`: Centralized client wrapper for making API calls to Groq and Gemini.
- `prompt_engine.py`: Manages the prompt templates used for BRD verification and FSD generation tasks.
- `helpers.py`: Various helper functions used across the application.
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

1. **Set up API Keys**: You will need API keys from Groq and Google (for Gemini). You can either set them in your environment variables or directly enter them in the application's **Settings** page.
2. **Run the Application**: Starting the Streamlit server.

   ```bash
   streamlit run app.py
   ```

3. **Navigate through the App**:
   - **Input**: Upload your BRD or paste the text directly.
   - **Verify**: Review the AI's analysis of your BRD to ensure it's ready for FSD generation.
   - **Generation**: Trigger the FSD generation process.
   - **Output**: Review the generated specifications and download the `.docx` file.

## 🔒 Configuration

API keys and specific generation settings can be configured via the **Settings** page within the app. The application primarily supports the following environment variables (which can also be placed in a `.env` file):

- `GROQ_API_KEY`: Your Groq API key.
- `GEMINI_API_KEY` (or `GOOGLE_API_KEY`): Your Google Gemini API key.

---
*Built with ❤️ using Streamlit and Generative AI.*
