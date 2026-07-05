"""
Scoring and Evaluation Module for AI Interview Agent

This module handles evaluation of individual user answers using the Groq API.
It parses the LLM grading details into a clean Python dictionary structure.
"""

import json
from prompt import ANSWER_SCORING_PROMPT
from utils import call_groq_api, clean_json_string

def evaluate_answer(question: str, user_answer: str, job_role: str, experience_level: str) -> dict:
    """
    Evaluates a candidate's answer using Groq API.
    
    Args:
        question (str): The question asked.
        user_answer (str): The candidate's response.
        job_role (str): The targeted job role.
        experience_level (str): The experience level (Fresher/Experienced).
        
    Returns:
        dict: A dictionary containing:
            - score (int): Grade out of 10
            - strengths (str): What was good about the answer
            - weaknesses (str): Constructive suggestions
            - suggested_answer (str): An exemplar answer
    """
    # Safeguard for empty answers
    if not user_answer.strip():
        return {
            "score": 0,
            "strengths": "None (No response provided).",
            "weaknesses": "No answer was typed. To receive points, you must write an answer.",
            "suggested_answer": "Please review core concepts corresponding to this question."
        }
        
    # Format the grading prompt
    formatted_prompt = ANSWER_SCORING_PROMPT.format(
        job_role=job_role,
        experience_level=experience_level,
        question=question,
        user_answer=user_answer
    )
    
    try:
        # Call Groq (with JSON mode enabled)
        raw_response = call_groq_api(formatted_prompt, json_mode=True)
        cleaned_response = clean_json_string(raw_response)
        
        # Parse the JSON response
        evaluation = json.loads(cleaned_response)
        
        # Validate structure and format
        score = evaluation.get("score", 0)
        # Ensure score is an integer and within bounds
        try:
            score = int(float(score))
            score = max(0, min(10, score))
        except (ValueError, TypeError):
            score = 5  # fallback midpoint
            
        return {
            "score": score,
            "strengths": evaluation.get("strengths", "No specific strengths noted."),
            "weaknesses": evaluation.get("weaknesses", "No specific weaknesses noted."),
            "suggested_answer": evaluation.get("suggested_answer", "No suggested answer generated.")
        }
        
    except Exception as e:
        # Fallback dictionary if API or parsing fails
        return {
            "score": 5,
            "strengths": "Evaluation parsing failed due to unexpected API response.",
            "weaknesses": f"Could not perform deep analysis. Error: {str(e)}",
            "suggested_answer": "Standard technical response could not be loaded."
        }
