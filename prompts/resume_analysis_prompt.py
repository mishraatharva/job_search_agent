RESUME_ANALYSIS_PROMPT= """
            From given Skills, Education and Experience, Analyze this resume information and provide specific, actionable suggestions 
            for improvement to make it more competitive in the job market.
            
            === RESUME DATA ===
            
            Skills: {skills}
            
            Education: {education}
            
            Experience: {experience}
            
            === ANALYSIS INSTRUCTIONS ===
            
            Provide a comprehensive analysis with the following clearly labeled sections:
            
            1. OVERALL ASSESSMENT
            • Strengths: Identify 3-5 strong aspects of the resume
            • Weaknesses: Point out 2-4 areas that need improvement
            • Industry fit: Based on the skills and experience, suggest 2-3 suitable industry sectors or job roles
            
            2. CONTENT IMPROVEMENTS
            • Achievements: Suggest how to better quantify results (provide 2-3 examples of how to reword vague statements)
            • Skills presentation: Advise on better organization or presentation of technical skills
            • Missing skills: Identify any critical skills that seem to be missing based on the experience described
            
            3. FORMAT SUGGESTIONS
            • Structure: Suggest optimal resume sections and ordering
            • Length: Advise on appropriate length based on experience level
            • Readability: Provide tips to improve scannability
            
            4. ATS OPTIMIZATION
            • Keywords: Suggest 5-7 additional keywords to include for better ATS matching
            • Formatting pitfalls: Identify any elements that could harm ATS parsing
            • File format recommendations
            
            Be extremely specific and actionable in your suggestions. Provide concrete examples where possible.
            Focus on transformative improvements rather than minor tweaks.
            """