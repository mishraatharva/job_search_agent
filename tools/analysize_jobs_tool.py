from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from config import GROQ_API_KEY, LLM_MODEL
import streamlit as st

class JobMatchInput(BaseModel):
    resume_data: dict = Field(..., description="Parsed resume data as a dict")
    job_data: dict = Field(..., description="Job description data as a dict")


class JobAnalyzer:
    def __init__(self,api_key):
        self.api_key = api_key
        self.llm = st.session_state.llm

    def __call__(self, resume_data, job_data):
        # You can replace this with your real logic
        return {
            "match_score": 82,
            "key_matches": ["Python", "Data Analysis"],
            "gaps": ["Cloud experience"],
            "recommendations": ["Add AWS project examples"]
        }
    
    def get_job_match_analysis(self, resume_data, job_data):
        """
        Analyze how well a resume matches a job description.
        
        Args:
            resume_data (dict): The parsed resume data
            job_data (dict): The job listing data
        
        Returns:
            dict: Match analysis with score and recommendations
        """
        if not self.api_key:
            return self._generate_basic_match_analysis(resume_data, job_data)
        
        try:
            # Initialize OpenAI client
            # client = OpenAI(api_key=self.api_key, model=self.model)
            
            # Extract relevant data
            skills = resume_data.get("skills", [])
            experience = resume_data.get("experience", [])
            job_title = job_data.get("title", "")
            job_description = job_data.get("description", "")
            
            # Create a prompt for matching analysis
            prompt = f"""
            Analyze how well this resume matches the job description and provide a detailed match analysis.
            
            === RESUME DATA ===
            Skills: {", ".join(skills)}
            
            Experience:
            {chr(10).join([f"- {exp}" for exp in experience])}
            
            === JOB DATA ===
            Title: {job_title}
            
            Description:
            {job_description}
            
            === ANALYSIS INSTRUCTIONS ===
            
            Provide a match analysis with the following components:
            
            1. MATCH SCORE: Calculate a percentage match (0-100%) based on how well the resume matches the job requirements.
            
            2. KEY MATCHES: List 3-5 specific skills or experiences from the resume that align well with the job requirements.
            
            3. GAPS: Identify 2-4 requirements in the job description that are not clearly demonstrated in the resume.
            
            4. RECOMMENDATIONS: Suggest 3-5 specific actions the candidate can take to better position themselves for this role.
            
            Format your response as a JSON with the following structure:
            {{
                "match_score": 85,
                "key_matches": ["match1", "match2", ...],
                "gaps": ["gap1", "gap2", ...],
                "recommendations": ["rec1", "rec2", ...]
            }}
            
            Ensure your analysis is specific, objective, and focused on the actual content in the resume and job description.
            """
            
            # Get analysis from OpenAI
            response = llm.create(
                model=self.model,
                prompt=prompt,
                max_tokens=1000,
                temperature=0.5
            )
            
            # Parse the response as JSON
            try:
                import json
                analysis = json.loads(response.choices[0].message.content.strip())
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                return {"match_analysis": response.choices[0].message.content.strip()}
            
        except Exception as e:
            print(f"Error in job match analysis: {e}")
            return self._generate_basic_match_analysis(resume_data, job_data)
    
    def _generate_basic_match_analysis(self, resume_data, job_data):
        """Generate basic job match analysis when OpenAI is not available."""
        skills = resume_data.get("skills", [])
        job_description = job_data.get("description", "").lower()
        
        # Count matching skills
        matching_skills = [skill for skill in skills if skill.lower() in job_description]
        
        # Calculate a simple match score
        match_score = min(len(matching_skills) * 10, 100) if skills else 50
        
        return {
            "match_score": match_score,
            "key_matches": matching_skills[:5],
            "gaps": ["Unable to analyze gaps without AI processing"],
            "recommendations": [
                "Review the job description and identify key requirements",
                "Customize your resume to highlight relevant skills and experience",
                "Add any missing skills that you possess but aren't in your resume"
            ]
        }
    
    
def return_job_match_tool():
    job_match_tool = StructuredTool.from_function(
        func=JobAnalyzer(api_key=GROQ_API_KEY),
        name="job_match_analysis",
        description="Analyze how well a resume matches a given job description.",
        args_schema=JobMatchInput
    )
    return job_match_tool