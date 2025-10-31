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