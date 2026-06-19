import os
import io
import time
import requests
import base64
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS
from dotenv import load_dotenv

# Auto-copy .env.example to .env if .env doesn't exist
if not os.path.exists(".env") and os.path.exists(".env.example"):
    try:
        with open(".env.example", "r", encoding="utf-8") as f_src:
            src_data = f_src.read()
        with open(".env", "w", encoding="utf-8") as f_dst:
            f_dst.write(src_data)
    except Exception:
        pass

# Load local environment variables from .env file
load_dotenv()
hf_token = os.getenv("HF_API_TOKEN", "")

# App Configuration
st.set_page_config(
    page_title="Jain Gyani Chatbot - जैन ज्ञानी",
    page_icon="☸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design System - Serene Saffron & Cream Jain Theme
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Mukta:wght@300;400;600;700;800&family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Global Styles & Text Visibility */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', 'Mukta', sans-serif;
        background: linear-gradient(135deg, #FAF6F0 0%, #FFFDF9 100%) !important;
        color: #2C2C2C !important;
    }
    
    /* Force high-contrast text color on chat messages, markdown, and paragraphs */
    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stMarkdownContainer"] li, 
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] ol,
    [data-testid="stMarkdownContainer"] ul,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] h5,
    [data-testid="stMarkdownContainer"] h6,
    label, legend, .stRadio label, .stCheckbox label {
        color: #2C2C2C !important;
    }

    /* Force button text contrast on suggestions */
    div[data-testid="stColumn"] button p {
        color: #4A3E31 !important;
    }
    div[data-testid="stColumn"] button:hover p {
        color: #B85A1C !important;
    }

    /* Sidebar specific text visibility styles */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] legend,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stCheckbox label {
        color: #4A3E31 !important;
    }
    
    /* Main Layout container padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Elegant Top Banner Card */
    .header-banner {
        background: linear-gradient(135deg, #FFF6EE 0%, #FFFDF9 100%);
        border: 2px solid #F5D3B3;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(184, 90, 28, 0.05);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .header-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 6px;
        background: linear-gradient(90deg, #FF9933, #D45D00, #FFAB58, #FF9933);
    }
    
    /* Header title styling */
    .jain-title {
        font-family: 'Mukta', sans-serif;
        font-weight: 800;
        color: #B85A1C; /* Darker spiritual saffron */
        margin: 0;
        font-size: 3.2rem;
        letter-spacing: 0.5px;
        text-shadow: 1px 1px 3px rgba(184, 90, 28, 0.1);
    }
    
    .jain-subtitle {
        font-family: 'Mukta', sans-serif;
        font-weight: 500;
        color: #7E7465;
        font-size: 1.3rem;
        margin-top: 8px;
        margin-bottom: 0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F8F1E7 !important;
        border-right: 1px solid #EADCCB;
        box-shadow: 2px 0 15px rgba(0,0,0,0.02);
    }

    /* Sidebar headers */
    .sidebar-section-header {
        font-family: 'Mukta', sans-serif;
        font-weight: 700;
        color: #B85A1C;
        font-size: 1.25rem;
        border-bottom: 2px solid #EADCCB;
        padding-bottom: 8px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    
    /* Serene Cards */
    .jain-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(245, 211, 179, 0.7);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(184, 90, 28, 0.04);
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
    }
    
    .jain-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(184, 90, 28, 0.08);
        border-color: rgba(255, 153, 51, 0.5);
    }

    /* Interactive Mantra Counter */
    .mantra-counter-card {
        background: linear-gradient(135deg, #FFF9F3 0%, #FFFDFB 100%);
        border: 1px solid #F5D3B3;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(184, 90, 28, 0.03);
    }

    .counter-display {
        font-size: 2.2rem;
        font-weight: 800;
        color: #D45D00;
        font-family: 'Outfit', sans-serif;
        margin: 10px 0;
        text-shadow: 1px 1px 2px rgba(212, 93, 0, 0.1);
    }
    
    /* Custom Chat bubbles */
    .stChatMessage {
        border-radius: 18px !important;
        margin-bottom: 18px !important;
        padding: 18px 22px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.015) !important;
        transition: all 0.3s ease !important;
        border: 1px solid transparent !important;
    }

    .stChatMessage:hover {
        box-shadow: 0 6px 20px rgba(184, 90, 28, 0.03) !important;
    }
    
    /* User chat bubble */
    [data-testid="chatAvatarIcon-user"], [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
        background-color: #E2725B !important; /* Terracotta */
    }
    
    /* Assistant chat bubble */
    [data-testid="chatAvatarIcon-assistant"], [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
        background-color: #FF9933 !important; /* Saffron */
    }
    
    /* Custom Buttons - Saffron style */
    .stButton>button {
        background: linear-gradient(135deg, #FF9933 0%, #D45D00 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-family: 'Mukta', sans-serif !important;
        font-size: 1rem !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(212, 93, 0, 0.18) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #FFAB58 0%, #E66500 100%) !important;
        box-shadow: 0 6px 18px rgba(212, 93, 0, 0.3) !important;
        transform: translateY(-2px) !important;
        color: white !important;
    }
    
    .stButton>button:active {
        transform: translateY(1px) !important;
    }

    /* Column buttons (for suggested questions) */
    div[data-testid="stColumn"] button {
        background: #FFFFFF !important;
        color: #4A3E31 !important;
        border: 1px solid #E2D3C1 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
        width: 100% !important;
        white-space: normal !important;
        height: auto !important;
        min-height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        line-height: 1.3 !important;
        font-size: 0.95rem !important;
        padding: 8px 12px !important;
        border-radius: 12px !important;
    }

    div[data-testid="stColumn"] button:hover {
        background: #FFF9F3 !important;
        color: #B85A1C !important;
        border-color: #FF9933 !important;
        box-shadow: 0 4px 12px rgba(184, 90, 28, 0.08) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Subtle Micro-animations */
    @keyframes pulse-saffron {
        0% { box-shadow: 0 0 0 0 rgba(255, 153, 51, 0.4); transform: scale(1); }
        70% { box-shadow: 0 0 0 10px rgba(255, 153, 51, 0); transform: scale(1.03); }
        100% { box-shadow: 0 0 0 0 rgba(255, 153, 51, 0); transform: scale(1); }
    }
    
    .spiritual-symbol {
        font-size: 2.6rem;
        color: #FF9933;
        text-align: center;
        animation: pulse-saffron 3s infinite ease-in-out;
        border-radius: 50%;
        width: 65px;
        height: 65px;
        line-height: 65px;
        margin: 0 auto 15px auto;
        background: white;
        border: 2px solid #F5D3B3;
        box-shadow: 0 4px 15px rgba(255, 153, 51, 0.15);
    }

    /* Style the text inputs */
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        border: 1px solid #EADCCB !important;
        border-radius: 8px !important;
        color: #2C2C2C !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #FF9933 !important;
        box-shadow: 0 0 0 1px #FF9933 !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------- SESSION STATE SETUP -----------------
JAIN_QUOTES = [
    {"devanagari": "परस्परोपग्रहो जीवानाम्।", "translation": "सभी जीव एक-दूसरे के पूरक हैं और परस्पर सहयोग करते हैं।"},
    {"devanagari": "अहिंसा परमो धर्मः।", "translation": "अहिंसा ही परम धर्म और सर्वोच्च कर्तव्य है।"},
    {"devanagari": "अप्पप्पा परमप्पा।", "translation": "प्रत्येक आत्मा स्वयं में परमात्मा बनने की क्षमता रखती है।"},
    {"devanagari": "मद-कषाय मुक्तिः परम सुखम्।", "translation": "क्रोध, मान, माया और लोभ का त्याग ही वास्तविक मोक्ष का मार्ग है।"},
    {"devanagari": "अनेकांतवादः - सत्य बहुआयामी अस्ति।", "translation": "सत्य के अनेक पहलू हैं, किसी एक विचार का हठ न करें।"}
]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "जय जिनेन्द्र। मैं 'जैन ज्ञानी' हूँ। मैं आपको जैन धर्म के सिद्धांतों, दर्शन, इतिहास और आचरण के बारे में जानकारी देने के लिए तत्पर हूँ। आप मुझसे अहिंसा, अनेकांतवाद, अपरिग्रह, कषाय, तीर्थंकर या किसी भी जैन ग्रंथ से संबंधित प्रश्न पूछ सकते हैं। आप अपना प्रश्न हिंदी या अंग्रेजी में लिख सकते हैं।",
            "audio": None
        }
    ]

if "quote_index" not in st.session_state:
    st.session_state.quote_index = 0

if "jap_count" not in st.session_state:
    st.session_state.jap_count = 0

# ----------------- SIDEBAR: CONFIGURATION -----------------
with st.sidebar:
    st.markdown('<div class="spiritual-symbol">☸️</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #B85A1C; font-family: Mukta; margin-top:0;'>जैन ज्ञानी सेटिंग्स</h2>", unsafe_allow_html=True)
    
    # # 1. API Token Panel (Hidden / Secured)
    # st.markdown('<div class="sidebar-section-header">🔑 API प्रमाणीकरण</div>', unsafe_allow_html=True)
    # env_token = os.getenv("HF_API_TOKEN", "")
    
    # if env_token:
    #     st.markdown(
    #         """
    #         <div style="background-color: #E8F5E9; border: 1px solid #C8E6C9; border-radius: 8px; padding: 10px 12px; margin-bottom: 12px;">
    #             <span style="color: #2E7D32; font-weight: 600; font-size: 0.9rem;">✅ API टोकन सक्रिय है</span><br/>
    #             <span style="color: #4CAF50; font-size: 0.8rem;">.env फ़ाइल से सुरक्षित रूप से लोड किया गया।</span>
    #         </div>
    #         """, 
    #         unsafe_allow_html=True
    #     )
    #     with st.expander("🔑 टोकन ओवरराइड करें (वैकल्पिक)"):
    #         hf_token = st.text_input(
    #             "नया Hugging Face API टोकन दर्ज करें:",
    #             value=env_token,
    #             type="password",
    #             help="यदि आप .env फ़ाइल के बजाय दूसरे टोकन का उपयोग करना चाहते हैं।"
    #         )
    # else:
    #     st.markdown(
    #         """
    #         <div style="background-color: #FFF3E0; border: 1px solid #FFE0B2; border-radius: 8px; padding: 10px 12px; margin-bottom: 12px;">
    #             <span style="color: #E65100; font-weight: 600; font-size: 0.9rem;">⚠️ प्रमाणीकरण की आवश्यकता है</span><br/>
    #             <span style="color: #EF6C00; font-size: 0.8rem;">चैट करने के लिए नीचे अपना API टोकन दर्ज करें।</span>
    #         </div>
    #         """, 
    #         unsafe_allow_html=True
    #     )
    #     hf_token = st.text_input(
    #         "Hugging Face API टोकन दर्ज करें:",
    #         value="",
    #         type="password",
    #         help="huggingface.co से निःशुल्क API टोकन प्राप्त करें।"
    #     )
    
    # # Alert user if token is missing
    # if not hf_token:
    #     st.warning("⚠️ चैट और Hugging Face TTS का उपयोग करने के लिए कृपया अपना Hugging Face API टोकन डालें। बिना टोकन के आप केवल Google TTS (gTTS) का ही उपयोग कर पाएंगे।")

    # 2. Interactive Mantra Jap Counter
    st.markdown('<div class="sidebar-section-header">📿 साधना (Practice)</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="mantra-counter-card">
            <div style="font-size: 0.9rem; color: #7E7465; font-weight: 600; margin-bottom: 2px;">णमोकार महामंत्र जाप काउंटर</div>
            <div class="counter-display">{st.session_state.jap_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    btn_col1, btn_col2 = st.columns([2, 1])
    if btn_col1.button("📿 जाप करें (Chant)", key="increment_jap"):
        st.session_state.jap_count += 1
        st.rerun()
    if btn_col2.button("🔄 रीसेट", key="reset_jap"):
        st.session_state.jap_count = 0
        st.rerun()

    # 3. LLM Model Selection
    st.markdown('<div class="sidebar-section-header">💬 भाषा मॉडल (LLM Model)</div>', unsafe_allow_html=True)
    model_choices = {
        "Qwen 2.5 7B Instruct (Recommended)": "Qwen/Qwen2.5-7B-Instruct",
        "Llama 3 8B Instruct": "meta-llama/Meta-Llama-3-8B-Instruct",
        "Mistral 7B Instruct v0.3": "mistralai/Mistral-7B-Instruct-v0.3"
    }
    selected_model_name = st.selectbox(
        "चैट मॉडल चुनें:",
        options=list(model_choices.keys()),
        index=0
    )
    selected_model_id = model_choices[selected_model_name]
    
    # 4. TTS Settings
    st.markdown('<div class="sidebar-section-header">🔊 वाक् सेटिंग (TTS Engine)</div>', unsafe_allow_html=True)
    tts_engine = st.radio(
        "आवाज का इंजन:",
        options=["Google TTS (gTTS) - Instant & Offline-like", "Hugging Face MMS TTS (mms-tts-hin) - Deep Neural"],
        index=0,
        help="Google TTS तेज़ है और इसके लिए किसी API टोकन की आवश्यकता नहीं होती है। Hugging Face MMS अधिक प्राकृतिक है लेकिन डाउनलोड/लोड होने में समय ले सकता है।"
    )
    
    autoplay_audio = st.checkbox("नया उत्तर आते ही स्वचालित रूप से बोलें (Autoplay)", value=True)
    
    # 5. Core Principles Quick Info
    st.markdown('<div class="sidebar-section-header">📜 जैन धर्म के मूल सिद्धांत</div>', unsafe_allow_html=True)
    st.markdown(
        """
        - **अहिंसा (Ahimsa)**: मन, वचन और काया से किसी भी जीव को कष्ट न पहुंचाना।
        - **अनेकांतवाद (Anekantavada)**: सत्य की बहुआयामी प्रकृति को स्वीकार करना (Non-absolutism)।
        - **अपरिग्रह (Aparigraha)**: इच्छाओं और संपत्ति का सीमित संचय।
        - **सत्य (Satya)**: प्रिय और हितकर सत्य बोलना।
        - **अचौर्य (Achaurya)**: बिना दी हुई वस्तु को ग्रहण न करना।
        - **ब्रह्मचर्य (Brahmacharya)**: संयमित जीवन जीना।
        """
    )

def render_speaking_ball(audio_bytes: bytes, engine_choice: str, autoplay: bool = False, index: int = 0, text: str = ""):
    """Renders a beautiful animated speaking ball that plays the TTS audio on click/autoplay (with browser synthesis fallback)."""
    # Clean text for JavaScript escaping
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ").replace("\r", "")
    
    audio_base64 = ""
    has_audio = "false"
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        has_audio = "true"
        
    mime_type = "audio/mp3" if "Google" in engine_choice else "audio/wav"
    autoplay_js = "true" if autoplay else "false"
    
    audio_source_tag = f'<source src="data:{mime_type};base64,{audio_base64}" type="{mime_type}">' if audio_bytes else ''
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: transparent;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            font-family: 'Mukta', 'Segoe UI', sans-serif;
            overflow: hidden;
        }}
        
        .speaking-container {{
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            padding: 8px 16px;
            background: rgba(255, 153, 51, 0.05);
            border: 1px dashed rgba(255, 153, 51, 0.3);
            border-radius: 50px;
            transition: all 0.3s ease;
            user-select: none;
            width: fit-content;
        }}
        
        .speaking-container:hover {{
            background: rgba(255, 153, 51, 0.1);
            border-color: rgba(255, 153, 51, 0.6);
            box-shadow: 0 4px 12px rgba(255, 153, 51, 0.08);
        }}
        
        .ball-wrapper {{
            position: relative;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* The speaking ball */
        .ball {{
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FF9933 0%, #E65C00 100%);
            box-shadow: 0 4px 10px rgba(230, 92, 0, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
            z-index: 2;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        
        /* Pulse waves (ripples) around the ball */
        .wave {{
            position: absolute;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: rgba(255, 153, 51, 0.45);
            z-index: 1;
            opacity: 0;
            transform: scale(1);
        }}
        
        /* When actively playing */
        .speaking .ball {{
            animation: bounce-pulse 0.8s infinite ease-in-out alternate;
            background: linear-gradient(135deg, #FF5E00 0%, #D43F00 100%);
            box-shadow: 0 4px 15px rgba(212, 63, 0, 0.5);
        }}
        
        .speaking .wave1 {{
            animation: ripple 1.6s infinite linear;
        }}
        
        .speaking .wave2 {{
            animation: ripple 1.6s infinite linear 0.5s;
        }}
        
        .speaking .wave3 {{
            animation: ripple 1.6s infinite linear 1s;
        }}
        
        /* Status text and audio visualizer bars */
        .info-panel {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .status-text {{
            font-size: 13px;
            font-weight: 600;
            color: #B85A1C;
            margin: 0;
            transition: color 0.3s ease;
        }}
        
        .speaking .status-text {{
            color: #D43F00;
            font-weight: 700;
        }}
        
        .sub-text {{
            font-size: 10px;
            color: #8C8070;
            margin: 2px 0 0 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* Visualizer lines inside the container */
        .visualizer {{
            display: none;
            align-items: flex-end;
            gap: 2.5px;
            height: 14px;
            margin-left: 10px;
        }}
        
        .speaking .visualizer {{
            display: flex;
        }}
        
        .bar {{
            width: 2.5px;
            height: 4px;
            background-color: #FF5E00;
            border-radius: 1px;
            animation: sound-wave 0.5s infinite ease-in-out alternate;
        }}
        
        .bar:nth-child(2) {{ animation-delay: 0.1s; }}
        .bar:nth-child(3) {{ animation-delay: 0.25s; }}
        .bar:nth-child(4) {{ animation-delay: 0.15s; }}
        .bar:nth-child(5) {{ animation-delay: 0.3s; }}
        
        /* Keyframes */
        @keyframes bounce-pulse {{
            0% {{ transform: scale(1); }}
            100% {{ transform: scale(1.15); }}
        }}
        
        @keyframes ripple {{
            0% {{
                transform: scale(1);
                opacity: 0.8;
            }}
            100% {{
                transform: scale(2.4);
                opacity: 0;
            }}
        }}
        
        @keyframes sound-wave {{
            0% {{ height: 4px; }}
            100% {{ height: 14px; }}
        }}
    </style>
    </head>
    <body>

    <div class="speaking-container" id="container-{index}" onclick="togglePlay()">
        <div class="ball-wrapper">
            <div class="wave wave1"></div>
            <div class="wave wave2"></div>
            <div class="wave wave3"></div>
            <div class="ball" id="ball-{index}">🔊</div>
        </div>
        <div class="info-panel">
            <p class="status-text" id="status-{index}">सुनने के लिए क्लिक करें</p>
            <p class="sub-text" id="subtext-{index}">ज्ञान वाणी</p>
        </div>
        <div class="visualizer">
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
        </div>
    </div>

    <audio id="audio-{index}">
        {audio_source_tag}
    </audio>

    <script>
        const audio = document.getElementById('audio-{index}');
        const container = document.getElementById('container-{index}');
        const ball = document.getElementById('ball-{index}');
        const statusText = document.getElementById('status-{index}');
        const subtext = document.getElementById('subtext-{index}');
        
        const hasAudioSource = {has_audio};
        let utterance = null;
        
        function togglePlay() {{
            if (hasAudioSource && audio) {{
                if (audio.paused) {{
                    audio.play().then(() => {{
                        container.classList.add('speaking');
                        ball.innerText = '🗣️';
                        statusText.innerText = 'ज्ञानी जी बोल रहे हैं...';
                        subtext.innerText = 'प्रवचन चालू है';
                    }}).catch(err => {{
                        console.error("Audio playback failed, falling back to synthesis:", err);
                        playViaSynthesis();
                    }});
                }} else {{
                    audio.pause();
                    stopPlayback();
                }}
            }} else {{
                if (window.speechSynthesis && window.speechSynthesis.speaking) {{
                    window.speechSynthesis.cancel();
                    stopPlayback();
                }} else {{
                    playViaSynthesis();
                }}
            }}
        }}
        
        function playViaSynthesis() {{
            if (!window.speechSynthesis) {{
                statusText.innerText = '⚠️ ब्राउज़र में वाक् असमर्थ';
                return;
            }}
            window.speechSynthesis.cancel();
            const textToSpeak = "{clean_text}";
            
            utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.lang = 'hi-IN';
            
            // Try to set a Hindi voice
            const voices = window.speechSynthesis.getVoices();
            const hindiVoice = voices.find(v => v.lang.includes('hi'));
            if (hindiVoice) {{
                utterance.voice = hindiVoice;
            }}
            
            utterance.onstart = function() {{
                container.classList.add('speaking');
                ball.innerText = '🗣️';
                statusText.innerText = 'ज्ञानी जी बोल रहे हैं... (ऑफ़लाइन)';
                subtext.innerText = 'प्रवचन चालू है';
            }};
            
            utterance.onend = function() {{
                stopPlayback();
            }};
            
            utterance.onerror = function(e) {{
                console.error("SpeechSynthesis error:", e);
                stopPlayback();
                statusText.innerText = '⚠️ वाक् असमर्थ';
            }};
            
            window.speechSynthesis.speak(utterance);
        }}
        
        function stopPlayback() {{
            container.classList.remove('speaking');
            ball.innerText = '🔊';
            statusText.innerText = 'सुनने के लिए क्लिक करें';
            subtext.innerText = 'ज्ञान वाणी';
        }}
        
        if (audio) {{
            audio.onended = function() {{
                stopPlayback();
            }};
        }}
        
        // Autoplay if requested
        if ({autoplay_js}) {{
            window.addEventListener('load', () => {{
                setTimeout(() => {{
                    togglePlay();
                }}, 400);
            }});
        }}
        
        // Load voices in background for speech synthesis compatibility
        if (window.speechSynthesis) {{
            window.speechSynthesis.getVoices();
            if (window.speechSynthesis.onvoiceschanged !== undefined) {{
                window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
            }}
        }}
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=75)

# ----------------- BACKEND FUNCTIONS -----------------

def get_offline_response(query: str) -> str:
    """Provides high quality offline answers for basic Jainism queries when internet is down."""
    q = query.lower()
    
    # Greetings
    if any(keyword in q for keyword in ["जय जिनेन्द्र", "pranam", "प्रणाम", "नमस्ते", "namaste", "hello", "hi", "jain", "जिनेन्द्र"]):
        return (
            "जय जिनेन्द्र! ऑफ़लाइन मोड (Offline Mode) में आपका स्वागत है। "
            "वर्तमान में आपका इंटरनेट कनेक्शन उपलब्ध नहीं है, इसलिए मैं सीमित ऑफ़लाइन ज्ञानकोश से उत्तर दे रहा हूँ। "
            "आप मुझसे निम्नलिखित विषयों पर प्रश्न पूछ सकते हैं:\n\n"
            "1. अहिंसा (Non-violence)\n"
            "2. तीर्थंकर (Tirthankaras)\n"
            "3. अनेकांतवाद (Anekantavada)\n"
            "4. णमोकार मंत्र (Namokar Mantra)\n"
            "5. अपरिग्रह (Non-possessiveness)"
        )
        
    # Ahimsa
    elif any(keyword in q for keyword in ["अहिंसा", "ahimsa", "violence", "जीव", "हिंसा"]):
        return (
            "अहिंसा जैन धर्म का सर्वोपरि और प्राणभूत सिद्धांत है—'अहिंसा परमो धर्मः'। "
            "मन, वचन और काय (शरीर) से किसी भी सूक्ष्म या स्थूल जीव को कष्ट न पहुँचाना अहिंसा है। "
            "जैन धर्म सिखाता है कि प्रत्येक जीव में आत्मा है और सबको जीने का समान अधिकार है। "
            "इसलिए जैन श्रावक रात्रि-भोजन का त्याग करते हैं और छने हुए पानी का उपयोग करते हैं ताकि सूक्ष्म जीवों की रक्षा हो सके।"
        )
        
    # Tirthankara
    elif any(keyword in q for keyword in ["तीर्थंकर", "tirthankar", "mahavira", "महावीर", "आदिनाथ", "ऋषभदेव", "पार्सनाथ", "parshvanath"]):
        return (
            "जैन धर्म में २४ तीर्थंकर हुए हैं। 'तीर्थंकर' वे परम पूज्य पुरुष होते हैं जिन्होंने कषायों (क्रोध, मान, माया, लोभ) को जीतकर "
            "केवलज्ञान (सर्वोच्च ज्ञान) प्राप्त किया और संसार रूपी समुद्र को पार करने के लिए धर्म-तीर्थ की स्थापना की। "
            "प्रथम तीर्थंकर भगवान ऋषभदेव (आदिनाथ जी) थे, २३वें भगवान पार्श्वनाथ जी थे और २४वें अंतिम तीर्थंकर भगवान महावीर स्वामी थे।"
        )
        
    # Anekantavada
    elif any(keyword in q for keyword in ["अनेकांतवाद", "anekantavada", "syadvada", "स्याद्वाद", "सत्य"]):
        return (
            "अनेकांतवाद (Anekantavada) जैन दर्शन का एक अत्यंत महत्वपूर्ण सिद्धांत है, जो सत्य की बहुआयामी प्रकृति को दर्शाता है। "
            "यह मानता है कि सत्य और वास्तविकता अत्यंत जटिल हैं और इसे केवल एक दृष्टिकोण से नहीं समझा जा सकता। "
            "विभिन्न कोणों से देखने पर सत्य के अलग-अलग रूप दिखाई देते हैं। इसे समझाने के लिए प्रायः छह नेत्रहीन पुरुषों और हाथी का उदाहरण दिया जाता है। "
            "यह सिद्धांत हमें दूसरों के विचारों को समझने, सहिष्णुता रखने और हठ का त्याग करने की प्रेरणा देता है।"
        )
        
    # Namokar Mantra
    elif any(keyword in q for keyword in ["णमोकार", "namokar", "मंत्र", "mantra", "navkar", "नवकार"]):
        return (
            "णमोकार मंत्र (महामंत्र) जैन धर्म का सबसे पवित्र और अनादि मूल मंत्र है:\n\n"
            "णमो अरिहंताणं (अरिहंतों को नमस्कार)\n"
            "णमो सिद्धाणं (सिद्धों को नमस्कार)\n"
            "णमो आयरियाणं (आचार्यों को नमस्कार)\n"
            "णमो उवज्झायाणं (उपाध्यायों को नमस्कार)\n"
            "णमो लोए सव्वसाहूणं (लोक के सभी साधुओं को नमस्कार)\n\n"
            "यह मंत्र किसी व्यक्ति विशेष को नहीं, बल्कि उनके भीतर प्रकट हुए दिव्य गुणों (पंच परमेष्ठी) को समर्पित है।"
        )
        
    # Aparigraha
    elif any(keyword in q for keyword in ["अपरिग्रह", "aparigraha", "desire", "संपत्ति", "attachment"]):
        return (
            "अपरिग्रह (Aparigraha) का अर्थ है इच्छाओं, आसक्तियों और भौतिक संपत्ति का सीमित संग्रह करना। "
            "जैन आचरण के अनुसार, आवश्यकता से अधिक वस्तुओं का संग्रह मानसिक अशांति और सामाजिक असमानता का कारण बनता है। "
            "अपरिग्रह का पालन करने से व्यक्ति में संतोष (Contentment) बढ़ता है और वह लोभ रूपी कषाय से मुक्त रहता है।"
        )
        
    # Default fallback
    return (
        "जय जिनेन्द्र। आपका नेटवर्क कनेक्शन बाधित है (ऑफ़लाइन मोड सक्रिय)। "
        "मैं आपके इस विशिष्ट प्रश्न का उत्तर देने में असमर्थ हूँ क्योंकि इसके लिए विस्तृत डेटाबेस या ऑनलाइन AI मॉडल की आवश्यकता है। "
        "कृपया इंटरनेट कनेक्शन चालू करें। ऑफ़लाइन रहते हुए आप मुझसे अहिंसा, अनेकांतवाद, अपरिग्रह, तीर्थंकर या णमोकार मंत्र के बारे में पूछ सकते हैं।"
    )

def query_hf_chat(token: str, model_id: str, prompt: str, chat_history: list) -> str:
    """Queries Hugging Face Serverless Inference API for chat completion."""
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Build proper system prompt dynamically matching target language
    is_hindi = any('\u0900' <= char <= '\u097f' for char in prompt)
    target_lang = "Hindi (written in Devanagari script)" if is_hindi else "English"
    
    system_prompt = (
        "You are 'Jain Gyani' (जैन ज्ञानी), a wise, peaceful, and compassionate scholar of Jainism (Jain Dharma). "
        "Your goal is to guide users on Jain philosophy, history, practices, ethics, and scriptures (like Tattvartha Sutra, Samaysara, etc.) in a respectful and authentic manner.\n\n"
        f"CRITICAL: The user has asked their question in {target_lang}. You MUST respond exclusively in {target_lang}. "
        f"Do not write in Hindi if the query is in English, and do not write in English if the query is in Hindi. "
        f"Your response must be entirely written in {target_lang}.\n\n"
        "Key Instructions:\n"
        "1. Tone: Speak with absolute humility, peace, and non-violence (Ahimsa). Use appropriate greetings if suitable.\n"
        "2. Core Philosophy: Anchor your answers in core Jain concepts: Ahimsa (non-violence), Anekantavada (multi-sided truth), Aparigraha (non-attachment), and the concept of Karma and Moksha.\n"
        "3. Accuracy: Distinguish between Digambara and Shvetambara perspectives when relevant, maintaining harmony and respect for both. Represent the beautiful wisdom of Jain scriptures.\n"
        "4. Length: Keep your responses concise and engaging (typically 3-5 sentences, max 150 words) so they are easy to listen to via Text-to-Speech. Avoid long bulleted lists unless explicitly requested."
    )
    
    # Format messages
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[:-1]:  # exclude the last user query we're about to add
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model_id,
        "messages": messages,
        "max_tokens": 600,
        "temperature": 0.7,
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        elif response.status_code == 503:
            # Model is loading
            wait_time = response.json().get("estimated_time", 20.0)
            st.info(f"🔄 मॉडल लोड हो रहा है... कृपया {int(wait_time)} सेकंड प्रतीक्षा करें।")
            time.sleep(min(wait_time, 5))
            # Retry once
            response = requests.post(url, headers=headers, json=payload, timeout=12)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            
        # Error details
        error_msg = response.json().get("error", "Unknown error occurred.")
        return f"त्रुटि (Error): {response.status_code} - {error_msg}."
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return "__OFFLINE_CONNECTION_ERROR__"
    except Exception as e:
        return f"त्रुटि (Error): {str(e)}."


def generate_audio_gtts(text: str) -> bytes:
    """Generates audio using Google Text-to-Speech (gTTS), auto-detecting Hindi or English."""
    try:
        clean_text = text.replace("*", "").replace("#", "").replace("-", " ")
        is_hindi = any('\u0900' <= char <= '\u097f' for char in clean_text)
        lang = 'hi' if is_hindi else 'en'
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        return None


def generate_audio_hf(token: str, text: str) -> bytes:
    """Generates Hindi audio using Meta's facebook/mms-tts-hin model on Hugging Face API."""
    url = "https://router.huggingface.co/hf-inference/models/facebook/mms-tts-hin"
    headers = {"Authorization": f"Bearer {token}"}
    
    clean_text = text.replace("*", "").replace("#", "").replace("-", " ")
    payload = {"inputs": clean_text}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            st.warning("⚠️ Hugging Face TTS मॉडल लोड हो रहा है। स्वचालित रूप से Google TTS का उपयोग कर रहे हैं...")
            return generate_audio_gtts(text)
        else:
            st.warning(f"⚠️ Hugging Face TTS अनुपलब्ध है ({response.status_code})। Google TTS का उपयोग कर रहे हैं...")
            return generate_audio_gtts(text)
    except Exception:
        return generate_audio_gtts(text)


def text_to_speech(text: str, engine_choice: str, token: str) -> bytes:
    """Helper to route speech request to chosen engine."""
    try:
        is_hindi = any('\u0900' <= char <= '\u097f' for char in text)
        # Force Google TTS for non-Hindi queries since facebook/mms-tts-hin is Hindi-only
        if not is_hindi or "Google TTS" in engine_choice or not token:
            return generate_audio_gtts(text)
        else:
            return generate_audio_hf(token, text)
    except Exception:
        return None

# ----------------- MAIN UI -----------------

if "is_offline" not in st.session_state:
    st.session_state.is_offline = False

st.markdown(
    """
    <div class="header-banner">
        <h1 class="jain-title">☸️ जैन ज्ञानी चैटबॉट</h1>
        <p class="jain-subtitle">जैन धर्म, दर्शन, इतिहास और आध्यात्मिक मार्गदर्शन के लिए आपका डिजिटल सहायक</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Scripture Quotes Card
quote_col, action_col = st.columns([4, 1])
with quote_col:
    current_quote = JAIN_QUOTES[st.session_state.quote_index]
    st.markdown(
        f"""
        <div class="jain-card" style="margin-top: 0px; border-left: 5px solid #FF9933; height: 100%;">
            <div style="font-size: 0.9rem; color: #FF9933; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 5px;">📜 आज का ज्ञान सूत्र (Wisdom Sutra of the Day)</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: #B85A1C; font-family: 'Mukta', sans-serif; margin-bottom: 5px;">"{current_quote['devanagari']}"</div>
            <div style="font-size: 1.0rem; color: #5D5447; font-style: italic;">अर्थ: {current_quote['translation']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with action_col:
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 ज्ञान सूत्र बदलें", key="next_quote"):
        st.session_state.quote_index = (st.session_state.quote_index + 1) % len(JAIN_QUOTES)
        st.rerun()

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Offline Warning Alert
if st.session_state.is_offline:
    st.markdown(
        """
        <div style="background-color: #FFF2E6; border: 1px solid #FFCC99; border-radius: 8px; padding: 12px; margin-bottom: 20px; color: #CC5500;">
            <strong>⚠️ ऑफ़लाइन मोड सक्रिय (Offline Mode Active):</strong> 
            हगिंग फेस सर्वर से कनेक्शन नहीं हो सका। आप अभी भी बुनियादी जैन दर्शन के प्रश्न पूछ सकते हैं और ब्राउज़र की आवाज़ सुन सकते हैं।
        </div>
        """,
        unsafe_allow_html=True
    )

# Preloaded Jainism Suggestion Questions
st.markdown("### 💡 उदाहरण प्रश्न (Suggested Questions)")
cols = st.columns(3)
suggestions = [
    "अहिंसा (Ahimsa) का जैन धर्म में क्या महत्व है?",
    "तीर्थंकर कौन होते हैं और कुल कितने तीर्थंकर हैं?",
    "अनेकांतवाद (Anekantavada) क्या है? सरल भाषा में बताएं।"
]

# We will populate buttons. If clicked, it sends the query automatically.
selected_suggestion = None
for i, suggestion in enumerate(suggestions):
    if cols[i].button(suggestion, key=f"sugg_{i}"):
        selected_suggestion = suggestion

# Display chat messages from session state
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Audio Player if available or generate on demand
        if message["role"] == "assistant":
            if message["audio"] is not None:
                render_speaking_ball(message["audio"], tts_engine, autoplay=False, index=index, text=message["content"])
            else:
                # Add a button to generate and play audio on demand
                if st.button("🔊 आवाज सुनें (Listen)", key=f"listen_{index}"):
                    with st.spinner("आवाज तैयार की जा रही है..."):
                        audio_data = text_to_speech(message["content"], tts_engine, hf_token)
                        if audio_data is None:
                            st.warning("⚠️ नेटवर्क अनुपलब्ध है। ब्राउज़र की स्थानीय आवाज़ का उपयोग किया जाएगा।")
                            audio_data = b"" # empty bytes indicates offline SpeechSynthesis
                        st.session_state.messages[index]["audio"] = audio_data
                        st.rerun()

# React to user input (either via suggestion button or chat input)
user_query = st.chat_input("अपना प्रश्न यहाँ लिखें...")
if selected_suggestion:
    user_query = selected_suggestion

if user_query:
    # Reset offline flag to attempt online reconnection
    st.session_state.is_offline = False
    
    # 1. Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # 2. Get chatbot response
    with st.chat_message("assistant"):
        with st.spinner("जैन ज्ञानी विचार कर रहे हैं..."):
            if not hf_token:
                response_text = (
                    "क्षमा करें, चैटबॉट से बात करने के लिए Hugging Face API टोकन की आवश्यकता है। "
                    "कृपया बाईं ओर (Sidebar) में अपना निःशुल्क API टोकन दर्ज करें। "
                    "टोकन मिलने तक, मैं आपको जैन धर्म का एक छोटा मंत्र सुना सकता हूँ: 'णमोकार मंत्र' जैन धर्म का सबसे पवित्र मंत्र है।"
                )
            else:
                response_text = query_hf_chat(
                    token=hf_token,
                    model_id=selected_model_id,
                    prompt=user_query,
                    chat_history=st.session_state.messages
                )
            
            # Switch to offline response database if network fails
            if response_text == "__OFFLINE_CONNECTION_ERROR__":
                st.session_state.is_offline = True
                response_text = get_offline_response(user_query)
            
            st.markdown(response_text)
            
            # Generate Audio
            audio_bytes = None
            if autoplay_audio:
                with st.spinner("आवाज तैयार की जा रही है..."):
                    audio_bytes = text_to_speech(response_text, tts_engine, hf_token)
                    if audio_bytes is None:
                        audio_bytes = b"" # empty bytes triggers offline SpeechSynthesis
                    current_idx = len(st.session_state.messages)
                    render_speaking_ball(audio_bytes, tts_engine, autoplay=True, index=current_idx, text=response_text)
            
            # Save Assistant Response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "audio": audio_bytes
            })
            
            # If autoplay was active, we already played it. If not, rerun to show the "Listen" button.
            if not autoplay_audio:
                st.rerun()
