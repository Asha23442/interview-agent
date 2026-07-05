# 💼 AI-Powered Technical Interview Agent

An advanced, production-grade AI-powered technical and behavioral Interview Agent developed for the **Rooman Technologies 24-Hour AI Agent Challenge**. Built with Python 3.11, Streamlit, and the Groq API (powered by the state-of-the-art **LLaMA-3.3-70B** model), this application conducts custom technical interviews, grades answers in real-time, compiles performance profiling reports, and saves them locally as structured JSON.

---

## 🌟 Key Features

1. **Candidate Profile Adaptation**: Customizes interview questions based on the candidate's Name, Target Job Role (e.g. Software Engineer, Data Scientist, Product Manager, or Custom write-ins), and Experience Track (Fresher vs. Experienced).
2. **Dynamic 5-Question Stepper**: Displays one question at a time with a sleek progress bar tracking completion.
3. **Real-time AI Grading & Feedback**: Uses Groq LLM to instantly grade responses on a 0-10 scale, compiling strengths, constructive weaknesses, and model answers (suggested responses) for each.
4. **Hiring Strategy Recommendation**: Auto-calculates overall score percentage and maps candidates to clear hiring categories:
   - **Hire** (Overall Score &ge; 8.0/10)
   - **Consider** (5.0/10 &le; Overall Score < 8.0/10)
   - **Reject** (Overall Score < 5.0/10)
5. **Robust Fallback Engine**: If the API key is missing, network cuts, or API rate limits are hit, the application falls back gracefully to a curated, high-quality offline technical questionnaire bank.
6. **Exportable Assessments**: Generates a standard JSON report in the `outputs/` folder and allows candidates or recruiters to download the report directly from the UI.
7. **Premium Glassmorphic Theme**: Designed with an ultra-modern dark theme, customized styling, smooth button transitions, and Google Fonts (`Inter` & `Outfit`).

---

## 📂 Project Architecture

```text
Interview-Agent/
│── app.py             # Entrypoint Streamlit application (UI and session states)
│── interview.py       # Core interview lifecycle controller & report generator
│── prompt.py          # Centralized LLM system and user prompt templates
│── scorer.py          # Intermediary evaluation module for scoring responses
│── utils.py           # API setups, folder initializers, and CSS injections
│── requirements.txt   # Third-party dependencies
│── README.md          # Implementation and developer instructions
│── .env.example       # Template configuration file for credentials
├── data/              # Stores candidate curriculum or documents (extendable)
├── outputs/           # Directory where final evaluation JSON reports are saved
└── screenshots/       # Contains application interface screenshots
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11.x installed on your local machine.

### 1. Clone or Copy the Repository
Navigate to the project root directory:
```bash
cd Interview-Agent
```

### 2. Set Up a Virtual Environment (Recommended)
Create and activate a virtual environment to isolate dependencies:

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries using pip:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to create your local environment variables configuration:
```bash
cp .env.example .env
```
Open the `.env` file and insert your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-specdec
```

---

## 💻 How to Run the Application

Start the Streamlit interface using:
```bash
streamlit run app.py
```
This will automatically launch the application in your default web browser (typically at `http://localhost:8501`).

---

## 📊 Sample Output Schema

When the interview is completed, a JSON report is automatically saved to the `outputs/` folder with the naming pattern: `outputs/<candidate_name>_<timestamp>.json`. Below is the standardized schema of the saved assessment:

```json
{
    "candidate_name": "Jane Doe",
    "job_role": "Software Engineer",
    "experience_level": "Experienced",
    "overall_score": 8.2,
    "percentage": 82.0,
    "final_recommendation": "Hire",
    "overall_strengths": "Jane exhibits robust clarity on system design...",
    "overall_weaknesses": "She could elaborate further on system optimization...",
    "evaluations": [
        {
            "question_number": 1,
            "question": "Explain the difference between REST and GraphQL...",
            "candidate_answer": "REST is resource-based where each URL represents...",
            "evaluation": {
                "score": 9,
                "strengths": "Accurately details resource architecture...",
                "weaknesses": "Missed mentioning standard schema definitions...",
                "suggested_answer": "REST utilizes standard HTTP verbs..."
            }
        }
        // ... Repeated for questions 2 to 5
    ],
    "timestamp": "2026-07-05 15:00:00"
}
```

---

## 🛠️ Developer Verification & Tests

Live : https://interview-agent-4bm5snsgltplemihvytlkn.streamlit.app/

To verify that the application modules are structurally sound, error-free, and import properly, run the verification test:
```bash
python test_import.py
```
This ensures all standard libraries, custom sub-modules (`prompt`, `utils`, `scorer`, `interview`), and class methods initialize seamlessly.
