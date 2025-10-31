from prompts.resume_analysis_prompt import RESUME_ANALYSIS_PROMPT
from langchain_core.tools import tool
import streamlit as st

## Error== llm
@tool
def analyze_resume(skills: str, education: str, experience: str):
    "This tool is use in case user is asking for resume analysis"
    # prompt = RESUME_ANALYSIS_PROMPT.format({"skills": skills, "education": education, "experience": experience})
    prompt = RESUME_ANALYSIS_PROMPT.format(skills=skills, education=education, experience=experience)

    try:
        analysis =  st.session_state.llm.invoke(prompt).content
    except:
        # Basic strengths analysis
        strengths = []
        if len(skills) >= 5:
            strengths.append("Good range of technical skills")
        if len(experience) >= 3:
            strengths.append("Solid work experience")
        if any("machine learning" in skill.lower() or "ai" in skill.lower() for skill in skills):
            strengths.append("Valuable AI/ML skills that are in high demand")
        
        analysis += "Strengths:\n"
        for strength in strengths or ["Resume contains some relevant skills"]:
            analysis += f"• {strength}\n"
        
        # Basic weaknesses analysis
        weaknesses = []
        if len(skills) < 5:
            weaknesses.append("Limited range of technical skills listed")
        if not any("python" in skill.lower() for skill in skills):
            weaknesses.append("Python (a widely used programming language) not explicitly listed")
        
        analysis += "\nWeaknesses:\n"
        for weakness in weaknesses or ["Consider adding more specific technical skills"]:
            analysis += f"• {weakness}\n"
        
        # Content improvements
        analysis += "\nCONTENT IMPROVEMENTS\n\n"
        analysis += "• Consider quantifying your achievements with specific metrics\n"
        analysis += "• Organize skills by category (programming languages, frameworks, tools)\n"
        analysis += "• Focus on highlighting relevant skills for your target roles\n"
        
        # Format suggestions
        analysis += "\nFORMAT SUGGESTIONS\n\n"
        analysis += "• Use a clean, ATS-friendly format with clear section headings\n"
        analysis += "• Ensure consistent formatting (bullet points, dates, etc.)\n"
        analysis += "• Keep resume to 1-2 pages maximum\n"
        
        # ATS optimization
        analysis += "\nATS OPTIMIZATION\n\n"
        analysis += "• Use keywords from job descriptions in your resume\n"
        analysis += "• Save your resume as a PDF to maintain formatting\n"
        analysis += "• Avoid tables, headers/footers, and images that can confuse ATS systems\n"
    
    return analysis