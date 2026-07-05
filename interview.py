"""
Interview Management Module for AI Interview Agent

This module handles the interview session lifecycle:
1. Question generation (with LLM and fallback options).
2. Compilation and saving of the final evaluation report.
3. Recommendations and summary generation using the Groq API.
"""

import os
import json
import datetime
from prompt import QUESTION_GENERATION_PROMPT, FINAL_SUMMARY_PROMPT
from utils import call_groq_api, clean_json_string, initialize_directories

# Default questions if API fails or is not configured
FALLBACK_QUESTIONS = {
    "software engineer": [
        "Explain the difference between REST and GraphQL, and key scenarios where you would choose one over the other.",
        "What are the differences between processes and threads, and how does Python's GIL impact multithreaded applications?",
        "How do you design a database schema for a high-traffic e-commerce system to prevent race conditions during checkout?",
        "Explain the concept of Big O notation and compare the time complexity of Quick Sort vs Merge Sort.",
        "Describe a time when you had to debug a difficult performance bottleneck in production. What was your process?"
    ],
    "data scientist": [
        "Explain the bias-variance tradeoff and how regularizations like L1 (Lasso) and L2 (Ridge) affect it.",
        "How do you handle missing values or highly imbalanced datasets in classification tasks?",
        "Explain how the Transformer architecture works and what makes its self-attention mechanism powerful.",
        "What is the difference between bagging and boosting algorithms? Give examples of both.",
        "Describe a scenario where a high accuracy score might be misleading, and what alternative metrics you would evaluate."
    ],
    "product manager": [
        "How do you prioritize a product roadmap when dealing with competing requests from engineering, sales, and executives?",
        "What metrics would you track to determine the success of a newly launched user onboarding flow?",
        "How do you handle a situation where customer feedback contradicts the quantitative data you have gathered?",
        "Explain how you would design a new subscription-based feature for a ride-sharing application.",
        "Describe a product launch that did not go as planned. What went wrong and what did you learn?"
    ]
}

def generate_questions(job_role: str, experience_level: str) -> list:
    """
    Generates exactly 5 technical and behavioral interview questions.
    Falls back to a high-quality static set of questions if Groq API fails.
    """
    formatted_prompt = QUESTION_GENERATION_PROMPT.format(
        job_role=job_role,
        experience_level=experience_level
    )
    
    try:
        # Request JSON array from API
        raw_response = call_groq_api(formatted_prompt, json_mode=True)
        cleaned = clean_json_string(raw_response)
        questions = json.loads(cleaned)
        
        # Ensure we have a list of strings
        if isinstance(questions, list) and len(questions) > 0:
            # Clean up the output to exactly 5 questions
            questions = [str(q) for q in questions if q][:5]
            
            # Pad if fewer than 5
            while len(questions) < 5:
                questions.append(f"Describe your experience building systems relevant to a {job_role} role.")
            return questions
            
    except Exception as e:
        # Suppress exception warning here to handle it gracefully with fallbacks
        pass
        
    # Fallback Mechanism
    role_key = job_role.lower()
    for key, fallback_list in FALLBACK_QUESTIONS.items():
        if key in role_key:
            return fallback_list
            
    # Generic backup questions if role is unique and API fails
    return [
        f"What are the core technical skills required for a successful {job_role} role, and how do you demonstrate them?",
        f"Describe a challenging project you worked on recently. What was your individual contribution?",
        "How do you keep your technical skills up-to-date with emerging trends in your industry?",
        "Explain how you handle working under tight deadlines or dealing with ambiguous requirements.",
        "Describe a time when you disagreed with a colleague on a technical decision. How was it resolved?"
    ]

def calculate_overall_score(evaluations: list) -> float:
    """
    Calculates the average score of all individual question evaluations.
    """
    if not evaluations:
        return 0.0
    scores = [eval_dict.get("score", 0) for eval_dict in evaluations]
    return round(sum(scores) / len(scores), 2)

def determine_recommendation(overall_score: float) -> str:
    """
    Computes hiring recommendation status based on the average score.
    """
    if overall_score >= 8.0:
        return "Hire"
    elif overall_score >= 5.0:
        return "Consider"
    else:
        return "Reject"

def generate_report(
    candidate_name: str,
    job_role: str,
    experience_level: str,
    questions: list,
    user_answers: list,
    evaluations: list
) -> dict:
    """
    Aggregates interview state, calls Groq API to compile final summary feedback,
    determines the overall score and hiring recommendation, and writes the JSON report.
    """
    initialize_directories()
    
    # Programmatic calculations
    overall_score = calculate_overall_score(evaluations)
    percentage = round(overall_score * 10, 1)
    recommendation = determine_recommendation(overall_score)
    
    # Construct transcript for final AI review
    transcript_list = []
    for i in range(len(questions)):
        q = questions[i]
        a = user_answers[i] if i < len(user_answers) else "No answer provided"
        e = evaluations[i] if i < len(evaluations) else {"score": 0, "strengths": "N/A", "weaknesses": "N/A"}
        transcript_list.append({
            "question_number": i + 1,
            "question": q,
            "candidate_answer": a,
            "score": e.get("score", 0),
            "strengths": e.get("strengths", ""),
            "weaknesses": e.get("weaknesses", "")
        })
        
    transcript_json_str = json.dumps(transcript_list, indent=2)
    
    # Request overall strengths & weaknesses from Groq
    overall_strengths = "Successfully answered standard technical interview questions."
    overall_weaknesses = "Some technical gaps or areas needing elaboration were identified in responses."
    
    try:
        formatted_prompt = FINAL_SUMMARY_PROMPT.format(
            candidate_name=candidate_name,
            job_role=job_role,
            experience_level=experience_level,
            transcript_json=transcript_json_str
        )
        # Call Groq for final summary
        summary_raw = call_groq_api(formatted_prompt, json_mode=True)
        summary_clean = clean_json_string(summary_raw)
        summary_data = json.loads(summary_clean)
        
        overall_strengths = summary_data.get("overall_strengths", overall_strengths)
        overall_weaknesses = summary_data.get("overall_weaknesses", overall_weaknesses)
    except Exception as e:
        # Fallback to local default aggregation if API summary fails
        strong_pts = [eval_dict.get("strengths") for eval_dict in evaluations if eval_dict.get("score", 0) >= 7]
        weak_pts = [eval_dict.get("weaknesses") for eval_dict in evaluations if eval_dict.get("score", 0) < 7]
        
        if strong_pts:
            overall_strengths = " - " + "\n - ".join(strong_pts[:3])
        if weak_pts:
            overall_weaknesses = " - " + "\n - ".join(weak_pts[:3])
            
    # Standardize individual evaluations inside the report
    individual_evaluations = []
    for i, q in enumerate(questions):
        ans = user_answers[i] if i < len(user_answers) else ""
        eval_item = evaluations[i] if i < len(evaluations) else {
            "score": 0,
            "strengths": "N/A",
            "weaknesses": "No evaluation completed.",
            "suggested_answer": "N/A"
        }
        individual_evaluations.append({
            "question_number": i + 1,
            "question": q,
            "candidate_answer": ans,
            "evaluation": eval_item
        })

    # Prepare complete report dictionary
    report = {
        "candidate_name": candidate_name,
        "job_role": job_role,
        "experience_level": experience_level,
        "overall_score": overall_score,
        "percentage": percentage,
        "final_recommendation": recommendation,
        "overall_strengths": overall_strengths,
        "overall_weaknesses": overall_weaknesses,
        "evaluations": individual_evaluations,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save the report as JSON file inside the outputs folder
    timestamp_slug = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_name = "".join([c if c.isalnum() else "_" for c in candidate_name.lower().replace(" ", "_")])
    filename = f"{sanitized_name}_{timestamp_slug}.json"
    filepath = os.path.join("outputs", filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving report to {filepath}: {str(e)}")
        
    return report
