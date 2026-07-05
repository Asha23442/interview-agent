"""
Utility Functions for AI Interview Agent

This module handles configuration loading, directory initialization, Groq API connections,
custom JSON sanitizing/parsing, and custom CSS styling injections for the Streamlit app.
"""

import os
import json
import re
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Constants
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-specdec")

def get_groq_client() -> Groq:
    """
    Initializes and returns the Groq client.
    First checks if the GROQ_API_KEY env variable or Streamlit secrets is set.
    """
    # Try getting key from environment variable
    api_key = os.getenv("GROQ_API_KEY")
    
    # Fallback to streamlit secrets if deployed/configured
    if not api_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
        
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Please create a '.env' file with "
            "GROQ_API_KEY=your_key or set it in your system environment variables."
        )
    return Groq(api_key=api_key)

def clean_json_string(raw_str: str) -> str:
    """
    Sanitizes raw LLM output to extract a valid JSON substring.
    Removes markdown code blocks (```json ... ```) and leading/trailing whitespace.
    """
    cleaned = raw_str.strip()
    
    # Remove markdown code blocks if present
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"```$", "", cleaned)
    cleaned = cleaned.strip()
    
    # Find the first occurrences of json start { or [ and last occurrences of } or ]
    start_match = re.search(r"[{\[]", cleaned)
    if start_match:
        start_idx = start_match.start()
        # Find matching close brace/bracket from end
        end_char = "}" if cleaned[start_idx] == "{" else "]"
        end_idx = cleaned.rfind(end_char)
        if end_idx != -1:
            cleaned = cleaned[start_idx:end_idx + 1]
            
    return cleaned

def call_groq_api(prompt: str, json_mode: bool = True) -> str:
    """
    Sends a prompt to the Groq API using the configured model and returns the response content.
    """
    try:
        client = get_groq_client()
        model_name = os.getenv("GROQ_MODEL", DEFAULT_MODEL)
        
        # Configure arguments
        kwargs = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        }
        
        # Groq support for response_format json
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        completion = client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content
    except Exception as e:
        # Provide helpful warning if it's a model error or key error
        st.error(f"Error communicating with Groq API: {str(e)}")
        raise e

def initialize_directories():
    """
    Ensures that output and data directories exist.
    """
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("data", exist_ok=True)

def inject_custom_css():
    """
    Injects custom Google Fonts and premium glassmorphic CSS styling
    into the Streamlit app.
    """
    st.markdown(
        """
        <style>
        /* Import premium Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
        
        /* Apply fonts globally */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
        }
        
        /* Background Styling: Sleek modern dark mode vibe with gradient elements */
        .stApp {
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            color: #c9d1d9;
        }
        
        /* Glassmorphic Container / Card styling */
        .glass-card {
            background: rgba(22, 27, 34, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(240, 246, 252, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        /* Glowing Card headers */
        .glass-header {
            background: linear-gradient(90deg, #1f6feb 0%, #8957e5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
            margin-bottom: 15px;
        }

        /* Success Score pill style */
        .score-pill {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 1rem;
            text-align: center;
        }
        
        .score-high {
            background-color: rgba(35, 134, 54, 0.2);
            color: #3fb950;
            border: 1px solid rgba(63, 185, 80, 0.4);
        }
        
        .score-mid {
            background-color: rgba(210, 153, 34, 0.2);
            color: #d29922;
            border: 1px solid rgba(210, 153, 34, 0.4);
        }
        
        .score-low {
            background-color: rgba(248, 81, 73, 0.2);
            color: #f85149;
            border: 1px solid rgba(248, 81, 73, 0.4);
        }

        /* Customize Streamlit Buttons */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #21262d 0%, #30363d 100%);
            color: #c9d1d9;
            border: 1px solid rgba(240, 246, 252, 0.1);
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        div.stButton > button:first-child:hover {
            background: linear-gradient(135deg, #1f6feb 0%, #8957e5 100%);
            color: #ffffff;
            border: 1px solid transparent;
            box-shadow: 0 8px 16px rgba(137, 87, 229, 0.3);
            transform: translateY(-2px);
        }

        /* Streamlit Input borders on focus */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            background-color: #0d1117 !important;
            color: #c9d1d9 !important;
            border: 1px solid rgba(240, 246, 252, 0.1) !important;
            border-radius: 8px !important;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #1f6feb !important;
            box-shadow: 0 0 0 2px rgba(31, 111, 235, 0.3) !important;
        }

        /* Center subheadings or tags styling */
        .subtitle {
            font-size: 1.1rem;
            color: #8b949e;
            margin-bottom: 25px;
        }
        
        /* Bullet point and lists */
        .highlight-list {
            margin-left: 20px;
            padding-left: 0;
        }
        
        .highlight-list li {
            margin-bottom: 8px;
            line-height: 1.5;
        }

        .highlight-list li strong {
            color: #58a6ff;
        }

        /* Divider styling */
        hr {
            border: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(240, 246, 252, 0.1), transparent);
            margin: 25px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
