"""
AI-Powered Interview Agent Streamlit Application

This is the main entry point for the application. It handles UI rendering,
state management, screen transitions, real-time progress tracking, and report generation.
"""

import json
import streamlit as st
from utils import inject_custom_css, initialize_directories
from scorer import evaluate_answer
from interview import generate_questions, generate_report, determine_recommendation

# Initialize directories
initialize_directories()

# Set up page configurations
st.set_page_config(
    page_title="AI Interview Agent - Rooman Challenge",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply premium styles
inject_custom_css()

# Initialize session state variables
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "interview_completed" not in st.session_state:
    st.session_state.interview_completed = False
if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "evaluations" not in st.session_state:
    st.session_state.evaluations = []
if "temp_answer" not in st.session_state:
    st.session_state.temp_answer = ""
if "is_graded" not in st.session_state:
    st.session_state.is_graded = False
if "current_evaluation" not in st.session_state:
    st.session_state.current_evaluation = None
if "final_report" not in st.session_state:
    st.session_state.final_report = None
if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""
if "job_role" not in st.session_state:
    st.session_state.job_role = ""
if "experience_level" not in st.session_state:
    st.session_state.experience_level = ""

# Sidebar for developer/API info
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/000000/artificial-intelligence.png", width=120)
    st.markdown("### Rooman AI Challenge")
    st.markdown("**AI Interview Agent v1.0**")
    st.markdown("Features:")
    st.markdown("- Tailored Question Bank")
    st.markdown("- Instant Grading & Feedback")
    st.markdown("- Strengths & Weaknesses Profiler")
    st.markdown("- Recommended Hiring Strategy")
    st.markdown("---")
    st.markdown("Created by Antigravity Python AI Specialist.")

# --- STEP 1: SETUP SCREEN ---
if not st.session_state.interview_started and not st.session_state.interview_completed:
    st.markdown("<div class='glass-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin-bottom:0;'>AI INTERVIEW AGENT</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Evaluate technical proficiency using LLaMA-3.3-70B model</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.form("setup_form"):
        st.markdown("### 📋 Candidate Information")
        
        name = st.text_input(
            "Candidate Full Name",
            placeholder="John Doe",
            help="Provide your name for the report"
        )
        
        # Job role selection with write-in option
        role_options = [
            "Software Engineer",
            "Data Scientist",
            "Product Manager",
            "DevOps Engineer",
            "Data Engineer",
            "Full Stack Developer",
            "Other"
        ]
        selected_role = st.selectbox("Job Role Target", options=role_options)
        
        custom_role = ""
        if selected_role == "Other":
            custom_role = st.text_input("Enter Job Role Name", placeholder="e.g. Cybersecurity Analyst")
            
        experience = st.select_slider(
            "Experience Level",
            options=["Fresher", "Experienced"],
            help="Fresher focuses on core concepts. Experienced targets architecture, design patterns, and case studies."
        )

        submitted = st.form_submit_button("Start Interview 🚀")
        
        if submitted:
            # Input validation
            if not name.strip():
                st.error("Please enter candidate name to proceed.")
            elif selected_role == "Other" and not custom_role.strip():
                st.error("Please specify the custom job role.")
            else:
                # Set role configuration
                final_role = custom_role.strip() if selected_role == "Other" else selected_role
                
                # Fetch questions (either via Groq or fallback)
                with st.spinner("Generating personalized questions based on profile..."):
                    questions = generate_questions(final_role, experience)
                
                # Update Session States
                st.session_state.candidate_name = name.strip()
                st.session_state.job_role = final_role
                st.session_state.experience_level = experience
                st.session_state.questions = questions
                st.session_state.interview_started = True
                st.session_state.current_question_idx = 0
                st.session_state.answers = []
                st.session_state.evaluations = []
                st.session_state.is_graded = False
                st.session_state.current_evaluation = None
                
                st.rerun()

# --- STEPS 2-6: QUESTION RUNNER ---
elif st.session_state.interview_started and not st.session_state.interview_completed:
    idx = st.session_state.current_question_idx
    total_q = len(st.session_state.questions)
    
    # Progress Calculation
    progress_val = float(idx) / float(total_q)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='margin:0; float:left; color:#1f6feb;'>Question {idx + 1} of {total_q}</h3>", unsafe_allow_html=True)
    st.markdown("<div style='clear:both;'></div>", unsafe_allow_html=True)
    st.progress(progress_val)
    
    # Display the current question
    q_text = st.session_state.questions[idx]
    st.markdown(f"<div style='font-size: 1.25rem; font-weight: 500; margin: 20px 0; line-height: 1.5;'>{q_text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Answer Input Box (disable if already graded for this question to prevent edits)
    answer_label = f"Type your answer for Question {idx + 1}:"
    user_ans = st.text_area(
        answer_label,
        key="temp_answer",
        height=150,
        disabled=st.session_state.is_graded,
        placeholder="Type your technical response here. Provide detailed examples where applicable..."
    )
    
    # Check score pill color style based on score value
    def get_score_pill_html(score):
        if score >= 8:
            return f"<span class='score-pill score-high'>Score: {score}/10</span>"
        elif score >= 5:
            return f"<span class='score-pill score-mid'>Score: {score}/10</span>"
        else:
            return f"<span class='score-pill score-low'>Score: {score}/10</span>"

    # Evaluation Feedback Card
    if st.session_state.is_graded and st.session_state.current_evaluation:
        eval_dict = st.session_state.current_evaluation
        score = eval_dict.get("score", 0)
        strengths = eval_dict.get("strengths", "N/A")
        weaknesses = eval_dict.get("weaknesses", "N/A")
        suggested = eval_dict.get("suggested_answer", "N/A")
        
        st.markdown("<div class='glass-card' style='border-left: 5px solid #1f6feb;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'>"
                    f"<h4 style='margin:0;'>Real-time AI Assessment</h4>"
                    f"{get_score_pill_html(score)}"
                    f"</div>", unsafe_allow_html=True)
        
        st.markdown(f"**💪 Strengths:**  \n{strengths}")
        st.markdown(f"**⚠️ Areas for Improvement:**  \n{weaknesses}")
        
        with st.expander("💡 Suggested Better Answer"):
            st.markdown(suggested)
            
        st.markdown("</div>", unsafe_allow_html=True)

    # Action Row
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Submit Answer Button (hide if already graded)
        if not st.session_state.is_graded:
            submit_btn = st.button("Submit Answer 📤", use_container_width=True)
            if submit_btn:
                if not user_ans.strip():
                    st.warning("Please type a response before submitting or click Skip.")
                else:
                    with st.spinner("Analyzing answer context..."):
                        evaluation = evaluate_answer(
                            question=q_text,
                            user_answer=user_ans,
                            job_role=st.session_state.job_role,
                            experience_level=st.session_state.experience_level
                        )
                        st.session_state.current_evaluation = evaluation
                        st.session_state.is_graded = True
                    st.rerun()

    with col2:
        # Skip Question Button (hide if already graded)
        if not st.session_state.is_graded:
            skip_btn = st.button("Skip Question ⏭️", use_container_width=True)
            if skip_btn:
                # Grade skipped answer as empty response
                evaluation = {
                    "score": 0,
                    "strengths": "N/A (Skipped by candidate).",
                    "weaknesses": "Question was skipped. No evaluation could be performed.",
                    "suggested_answer": "Review concepts related to this question before the next attempt."
                }
                st.session_state.current_evaluation = evaluation
                st.session_state.temp_answer = "Skipped"
                st.session_state.is_graded = True
                st.rerun()

    with col3:
        # Next / Finish Button (only show if graded)
        if st.session_state.is_graded:
            is_last = (idx == total_q - 1)
            btn_label = "Finish Interview 🏁" if is_last else "Next Question ➡️"
            
            action_btn = st.button(btn_label, use_container_width=True)
            if action_btn:
                # Record answer and evaluation
                st.session_state.answers.append(st.session_state.temp_answer)
                st.session_state.evaluations.append(st.session_state.current_evaluation)
                
                # Move to next state
                if is_last:
                    with st.spinner("Compiling results and generating executive report..."):
                        report = generate_report(
                            candidate_name=st.session_state.candidate_name,
                            job_role=st.session_state.job_role,
                            experience_level=st.session_state.experience_level,
                            questions=st.session_state.questions,
                            user_answers=st.session_state.answers,
                            evaluations=st.session_state.evaluations
                        )
                        st.session_state.final_report = report
                        st.session_state.interview_completed = True
                        st.session_state.interview_started = False
                else:
                    st.session_state.current_question_idx += 1
                    # Reset current evaluation state
                    st.session_state.is_graded = False
                    st.session_state.current_evaluation = None
                    st.session_state.temp_answer = ""
                st.rerun()

# --- STEP 7: SUMMARY & FINAL REPORT SCREEN ---
elif st.session_state.interview_completed and st.session_state.final_report:
    # Trigger Streamlit celebration
    st.balloons()
    
    report = st.session_state.final_report
    avg_score = report.get("overall_score", 0.0)
    percentage = report.get("percentage", 0.0)
    recommendation = report.get("final_recommendation", "Consider")
    
    st.markdown("<div class='glass-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #58a6ff; margin:0;'>INTERVIEW COMPLETED</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;'>Thank you for participating. The executive assessment has been completed.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Recommendation color formatting
    rec_style = ""
    if recommendation == "Hire":
        rec_style = "background-color: rgba(35, 134, 54, 0.2); color: #3fb950; border: 1px solid #3fb950;"
    elif recommendation == "Consider":
        rec_style = "background-color: rgba(210, 153, 34, 0.2); color: #d29922; border: 1px solid #d29922;"
    else:
        rec_style = "background-color: rgba(248, 81, 73, 0.2); color: #f85149; border: 1px solid #f85149;"
        
    # High-level Metrics Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.9rem; color:#8b949e;'>Average Score</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:2.2rem; font-weight:800; color:#58a6ff;'>{avg_score} <span style='font-size:1rem; color:#8b949e;'>/ 10</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.9rem; color:#8b949e;'>Percentage</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:2.2rem; font-weight:800; color:#8957e5;'>{percentage}%</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='glass-card' style='text-align:center; height:100%;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.9rem; color:#8b949e;'>Recommendation</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-top: 8px; padding: 6px 12px; border-radius: 8px; font-weight: 700; font-size:1.4rem; text-align:center; {rec_style}'>{recommendation}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Candidate details card
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 👤 Assessment Details")
    st.markdown(f"**Candidate Name:** {report.get('candidate_name')}")
    st.markdown(f"**Target Role:** {report.get('job_role')}")
    st.markdown(f"**Experience Track:** {report.get('experience_level')}")
    st.markdown(f"**Evaluation Date:** {report.get('timestamp')}")
    st.markdown("</div>", unsafe_allow_html=True)

    # AI Summary Strengths & Weaknesses
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🏆 Executive Feedback Summary")
    
    st.markdown("#### **Key Strengths**")
    st.write(report.get("overall_strengths"))
    
    st.markdown("#### **Areas for Development**")
    st.write(report.get("overall_weaknesses"))
    st.markdown("</div>", unsafe_allow_html=True)

    # Question Breakdown Section
    st.markdown("### 📑 Detailed Performance Breakdown")
    for item in report.get("evaluations", []):
        q_num = item.get("question_number")
        question = item.get("question")
        cand_ans = item.get("candidate_answer")
        eval_info = item.get("evaluation", {})
        score = eval_info.get("score", 0)
        
        # Color coding score tags for headers
        score_tag = ""
        if score >= 8:
            score_tag = f"<span style='color:#3fb950; font-weight:bold;'>[Score: {score}/10]</span>"
        elif score >= 5:
            score_tag = f"<span style='color:#d29922; font-weight:bold;'>[Score: {score}/10]</span>"
        else:
            score_tag = f"<span style='color:#f85149; font-weight:bold;'>[Score: {score}/10]</span>"

        with st.expander(f"Question {q_num}: {question[:60]}... {score_tag}"):
            st.markdown(f"**Full Question:**  \n{question}")
            st.markdown(f"**Candidate Answer:**  \n*{cand_ans}*")
            st.markdown("---")
            st.markdown(f"**Strengths:**  \n{eval_info.get('strengths')}")
            st.markdown(f"**Weaknesses:**  \n{eval_info.get('weaknesses')}")
            st.markdown(f"**Suggested Better Answer:**  \n{eval_info.get('suggested_answer')}")

    # Action Panel
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        # Convert report to JSON string for download
        json_data = json.dumps(report, indent=4, ensure_ascii=False)
        st.download_button(
            label="Download JSON Report 💾",
            data=json_data,
            file_name=f"interview_report_{report.get('candidate_name').replace(' ', '_').lower()}.json",
            mime="application/json",
            use_container_width=True
        )
    with col2:
        restart_btn = st.button("Start New Interview 🔄", use_container_width=True)
        if restart_btn:
            # Reset all session states
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
