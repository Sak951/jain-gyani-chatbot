# Jain Chatbot (जैन ज्ञानी) with Hindi TTS

A modern, responsive Python Streamlit chatbot utilizing free Hugging Face models to discuss Jain philosophy, history, and practices. Responses are generated in Hindi (written in Devanagari script) and can be read aloud using Hindi Text-to-Speech (TTS).

## Features

- **Jain Gyani Chatbot**: High-quality conversations grounded in Jain scriptures, principles (Ahimsa, Anekantavada, Aparigraha, etc.), and lifestyle choices.
- **Multilingual Input / Hindi Output**: Type questions in Hindi (e.g., "अहिंसा क्या है?") or English (e.g., "What is Ahimsa?"), and get standard, respectful responses in Hindi.
- **Hindi Text-to-Speech**:
  - **Meta MMS TTS (`facebook/mms-tts-hin`)**: Advanced neural text-to-speech model from Hugging Face.
  - **Google TTS (`gTTS`)**: Lightweight, robust, and zero-key alternative.
- **Customizable Styling**: A beautiful Jain-themed user interface, complete with peaceful colors, typography, micro-interactions, and a sidebar for configuration.

## Setup Instructions

1. **Install Dependencies**:
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key (Optional)**:
   - Copy `.env.example` to `.env`.
   - Add your Hugging Face Access Token to the `.env` file, or simply enter it directly in the application's sidebar.
   - *Note: Getting a Hugging Face token is 100% free and takes 1 minute on [huggingface.co](https://huggingface.co/).*

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Design System & Theme

- **Primary Colors**: Deep saffron/ochre (peaceful, spiritual tone) combined with soft cream/sand backgrounds.
- **Typography**: Uses clean sans-serif/Hindi supported fonts for readability.
- **UI Elements**: Rounded cards, glassmorphic panels, and animated transitions for an extremely premium feel.
