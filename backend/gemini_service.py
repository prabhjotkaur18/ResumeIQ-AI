import os
import json
from dotenv import load_dotenv
from google import genai

# Load API Key
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_resume(resume_text, job_role):
    prompt = f"""
You are an expert ATS Resume Analyzer.

Analyze the following resume for the role of {job_role}.

Return ONLY valid JSON in this exact format:

{{
    "ats_score": 0,
    "resume_score": 0,
    "skills_found": [],
    "missing_skills": [],
    "career_recommendation": "",
    "learning_roadmap": [],
    "interview_questions": [],
    "resume_suggestions": []
}}

Resume:

{resume_text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    text = response.text.strip()

    # Remove Markdown code fences if Gemini adds them
    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()
    elif text.startswith("```"):
        text = text.replace("```", "").strip()

    try:
        return json.loads(text)

    except Exception:
        return {
            "ats_score": 0,
            "resume_score": 0,
            "skills_found": [],
            "missing_skills": [],
            "career_recommendation": text,
            "learning_roadmap": [],
            "interview_questions": [],
            "resume_suggestions": []
        }