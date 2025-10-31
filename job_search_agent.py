import sys
sys.stdout.reconfigure(encoding='utf-8')

import streamlit as st
import pandas as pd
import os
import json
import tempfile
import PyPDF2
import docx
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_groq import ChatGroq
# from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
load_dotenv()

# Create directories if they don't exist
os.makedirs("agents", exist_ok=True)
os.makedirs("utils", exist_ok=True)
os.makedirs("saved_jobs", exist_ok=True)
os.makedirs("saved_interviews", exist_ok=True)

# Import the UI utilities for improved display
from ui_utils import (
    display_formatted_analysis, 
    display_resume_analysis_summary,
    display_extracted_information,
    extract_agent_output,
    # format_job_description,
    # display_matching_skills,
    clean_jobs_result,
    apply_styling
)

# Import job storage functions
from utils.job_storage import (
    # save_job_to_local,
    load_saved_jobs,
    # remove_saved_job
)

# Import configuration
from config import COLORS, JOB_PLATFORMS

# Set page configuration with professional appearance
st.set_page_config(
    page_title="Professional Job Search Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS to enhance the UI with a professional balanced style
def apply_styling():
    st.markdown(f"""
    <style>
        /* Global font styling */
        * {{
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important;
        }}
        
        /* Main header styling - like the "You have 1 saved jobs" header */
        h1, h2, .main-header {{
            color: white !important;
            background-color: {COLORS['primary']} !important;
            padding: 20px !important;
            border-radius: 8px !important;
            margin-bottom: 20px !important;
            font-weight: bold !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        }}
        
        /* Blue header panels styling - consistent across all pages */
        div[style*="background-color: {COLORS['primary']}"],
        div[style*="background-color: rgb(28, 78, 128)"],
        [data-testid="stForm"] h3,
        .blue-header {{
            color: white !important;
            font-size: 1.2rem !important;
            font-weight: bold !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
            padding: 15px !important;
            border-radius: 6px !important;
            margin-bottom: 15px !important;
            background-color: {COLORS['primary']} !important;
        }}
        
        /* Fix for text in blue panels */
        div[style*="background-color: {COLORS['primary']}"] p,
        div[style*="background-color: {COLORS['primary']}"] span,
        div[style*="background-color: {COLORS['primary']}"] h3,
        div[style*="background-color: {COLORS['primary']}"] h4,
        div[style*="background-color: {COLORS['primary']}"] div {{
            color: white !important;
            font-weight: bold !important;
        }}
        
        /* Buttons styled like "Apply to this job" button */
        .stButton>button,
        button[kind="primary"] {{
            background-color: {COLORS["accent3"]} !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            border: none !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            font-size: 16px !important;
            height: auto !important;
        }}
        
        .stButton>button:hover,
        button[kind="primary"]:hover {{
            background-color: #E67E22 !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
            transform: translateY(-1px) !important;
        }}
        
        /* Tables like in Saved Jobs tab */
        table, .dataframe, [data-testid="stTable"] {{
            width: 100% !important;
            border-collapse: collapse !important;
            margin-bottom: 20px !important;
            border-radius: 4px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        }}
        
        /* Table headers like "Saved Jobs" tab */
        th, thead tr th {{
            background-color: #222222 !important;
            color: white !important;
            font-weight: bold !important;
            padding: 12px 8px !important;
            text-align: left !important;
            border: none !important;
        }}
        
        /* Table cells like "Saved Jobs" tab */
        td, tbody tr td {{
            padding: 12px 8px !important;
            border-bottom: 1px solid #EEEEEE !important;
            background-color: white !important;
            color: black !important;
        }}
        
        /* Alternate row styling */
        tbody tr:nth-child(even) td {{
            background-color: #f9f9f9 !important;
        }}
        
        /* Main navigation tabs */
        div[data-baseweb="tab-list"] {{
            gap: 0 !important;
            background-color: {COLORS["background"]} !important;
            padding: 10px !important;
            border-radius: 12px !important;
            display: flex !important;
            justify-content: space-between !important;
            width: 100% !important;
            margin-bottom: 20px !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1) !important;
        }}
        
        div[data-baseweb="tab-list"] button {{
            flex: 1 !important;
            text-align: center !important;
            margin: 0 5px !important;
            height: 60px !important;
            font-size: 16px !important;
            background-color: rgba(255, 255, 255, 0.7) !important;
            color: {COLORS["primary"]} !important;
            border-radius: 8px !important;
            border: 1px solid rgba(0,0,0,0.05) !important;
            transition: all 0.3s ease !important;
        }}
        
        div[data-baseweb="tab-list"] button[aria-selected="true"] {{
            background-color: {COLORS["primary"]} !important;
            color: white !important;
            border-bottom: 3px solid {COLORS["accent3"]} !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            transform: translateY(-2px) !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# if "llm" not in st.session_state:
#     st.session_state.llm = ChatGroq(model="openai/gpt-oss-20b")

if "llm" not in st.session_state:
    st.session_state.llm = ChatOpenAI(model="gpt-4")

# Apply custom styling
apply_styling()

# Initialize tools and agents
@st.cache_resource
def load_resources():
    """Load and cache all required resources."""
    from utils.resume_parser import ResumeParser
    from utils.serp_api_searcher import SerpApiSearcher
    from utils.resume_keyword_extractor import ResumeKeywordExtractor
    from agents.job_agent import get_job_search_agent
    
    resume_parser = ResumeParser()
    serp_api_searcher = SerpApiSearcher()
    keyword_extractor = ResumeKeywordExtractor()
    job_search_agent = get_job_search_agent(st.session_state.llm)
    
    return {
        "resume_parser": resume_parser,
        "job_search_agent": job_search_agent,
        "serp_api_searcher": serp_api_searcher,
        "keyword_extractor": keyword_extractor
    }

# Load resources
resources = load_resources()

# Application header with gradient using color palette
st.markdown(f"""
<div style='text-align:center; padding: 1.5rem 0; 
background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}, {COLORS["tertiary"]}); 
border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
    <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>
    Professional Job Search Assistant</h1>
    <p style='color: white; font-size: 1.2rem; font-weight: 500; margin: 0.5rem 2rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);'>
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    AI-powered job search</span> 
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    Resume analysis</span> 
    <span style='background-color: rgba(0,0,0,0.15); padding: 4px 12px; border-radius: 20px; margin: 0 5px;'>
    Interview preparation</span>
    </p>
</div>
""", unsafe_allow_html=True)

# Session state initialization
if "resume_data" not in st.session_state:
    st.session_state.resume_data = {}

if "job_results" not in st.session_state:
    st.session_state.job_results = []

if "selected_job" not in st.session_state:
    st.session_state.selected_job = None

if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = None

if "saved_jobs" not in st.session_state:
    st.session_state.saved_jobs = load_saved_jobs()

# Create main navigation tabs
tabs = st.tabs([
    "Resume Analysis", 
    "Job Search"
    # "Saved Jobs"
])

# # Create main navigation tabs
# tabs = st.tabs([
#     "📄 Resume Analysis", 
#     "🔍 Job Search", 
#     "💼 Saved Jobs"
# ])

# Make sure the correct tab is active if coming from another section
if hasattr(st.session_state, 'active_tab'):
    active_tab_index = st.session_state.active_tab
    # We can't directly set the active tab, so we'll rely on session state changes to indicate
    # which tab should be active when the page reruns


# Tab 1: Resume Analysis
with tabs[0]:
    st.header("Resume Analysis")
    
    # Create two columns for upload options
    col1, col2 = st.columns(2)
    
    with col1:
        # Resume upload section
        st.subheader("Upload Resume")
        st.markdown(f"""
        <div style="background-color: {COLORS["panel_bg"]}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <p style="margin-bottom: 10px;">Upload your resume in PDF, DOCX, or TXT format.</p>
        <p>We'll analyze your resume and extract key information to help you find matching jobs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Resume file uploader
        resume_file = st.file_uploader("Upload your resume", type=["pdf", "txt", "docx"], key="resume_uploader")
        
        # Process uploaded resume
        if resume_file is not None:
            with st.spinner("Analyzing your resume..."):
                try:
                    # Load resume parser
                    resume_parser = resources["resume_parser"]
                    
                    # Save uploaded file to a temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as temp_file:
                        temp_file.write(resume_file.getbuffer())
                        temp_path = temp_file.name
                    
                    # Read the file content
                    try:
                        # For PDF files
                        if temp_path.endswith('.pdf'):
                            with open(temp_path, 'rb') as f:
                                pdf_reader = PyPDF2.PdfReader(f)
                                extracted_text = ""
                                for page_num in range(len(pdf_reader.pages)):
                                    page = pdf_reader.pages[page_num]
                                    extracted_text += page.extract_text() + "\n"
                        
                        # For DOCX files
                        elif temp_path.endswith('.docx'):
                            doc = docx.Document(temp_path)
                            extracted_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                        
                        # For TXT files
                        else:
                            with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                                extracted_text = f.read()
                        
                        # Clean up the temporary file
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                        
                        # If we got text, parse it
                        if extracted_text:
                            
                            # Parse resume and extract info
                            resume_data = resume_parser.parse_resume(extracted_text)
                            skills = ", ".join(resume_data.get("skills", []))

                            education_list = resume_data.get("education", [])
                            education = "\n".join([f"- {edu}" for edu in education_list])

                            experience_list = resume_data.get("experience", [])
                            experience = "\n".join([f"- {exp}" for exp in experience_list])
                            
                            # Get agent
                            agent_executor = resources["job_search_agent"]
                            input_message = {
                                                "role": "user",
                                                "content": f"Please analyze this resume with the following details:\n\nSkills: {skills}\n\nEducation:\n{education}\n\nExperience:\n{experience}"
                                            }

                            response = agent_executor.invoke({"messages": [input_message]})
                            
                            # Store resume data and analysis in session state
                            st.session_state.resume_data = resume_data
                            st.session_state.resume_data["analysis"] = response
                            st.session_state.resume_data["raw_text"] = extracted_text
                            
                            st.success("Resume analysis complete! Review the extracted information and analysis below.")
                        else:
                            st.error("Could not extract text from the uploaded file.")
                    except Exception as file_error:
                        st.error(f"Error processing file: {str(file_error)}")
                        st.info("If the error persists, try uploading a different file format or check if the resume is properly formatted.")
                        
                except Exception as e:
                    st.error(f"Error analyzing resume: {str(e)}")
                    st.info("If the error persists, try uploading a different file format or check if the resume is properly formatted.")
    

    with col2:
        # Resume tips and advice
        st.subheader("Resume Tips")
        st.markdown(f"""
        <div style="background-color: {COLORS["accent1"]}; color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h4 style="margin-top: 0; color: white;">Key Resume Components:</h4>
        <ul style="margin-bottom: 0;">
        <li><strong>Clear contact information</strong> - Make it easy for employers to reach you</li>
        <li><strong>Relevant skills section</strong> - Highlight technical and soft skills</li>
        <li><strong>Quantified achievements</strong> - Use numbers to demonstrate impact</li>
        <li><strong>ATS-friendly format</strong> - Use standard headings and keywords</li>
        <li><strong>Consistent formatting</strong> - Maintain professional appearance</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # ATS optimization tips
        st.markdown(f"""
        <div style="background-color: {COLORS["secondary"]}; color: white; padding: 15px; border-radius: 8px; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <h4 style="margin-top: 0; color: white;">ATS Optimization Tips:</h4>
        <ul style="margin-bottom: 0;">
        <li>Use keywords from the job description</li>
        <li>Avoid tables, headers/footers, and images</li>
        <li>Use standard section headings</li>
        <li>Submit in PDF format when possible</li>
        <li>Keep formatting simple and clean</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Display resume analysis results if available
    if "resume_data" in st.session_state and st.session_state.resume_data:
        st.markdown("---")
        
        # Create tabs for different views of resume data
        resume_tabs = st.tabs(["Summary", "Skills & Experience", "Analysis", "Raw Text"])
        
        # Tab 1: Summary view
        with resume_tabs[0]:
            display_resume_analysis_summary(st.session_state.resume_data)
        
        # Tab 2: Skills & Experience
        with resume_tabs[1]:
            display_extracted_information(st.session_state.resume_data)
        
        # Tab 3: Analysis
        with resume_tabs[2]:
            if "analysis" in st.session_state.resume_data:
                final_text = extract_agent_output(st.session_state.resume_data["analysis"])
                display_formatted_analysis(final_text)
            else:
                st.info("No detailed analysis available. Please re-upload your resume to generate an analysis.")
        
        # Tab 4: Raw Text
        with resume_tabs[3]:
            if "raw_text" in st.session_state.resume_data:
                st.text_area("Extracted Text", st.session_state.resume_data["raw_text"], height=400, disabled=True)
            else:
                st.info("Raw text not available.")
        
        # # Add a section to explain resume improvement suggestions
        # with st.expander("Resume Improvement Recommendations", expanded=False):
        #     st.markdown(f"""
        #     <div style="background-color: {COLORS["panel_bg"]}; padding: 15px; border-radius: 8px; margin: 10px 0;">
        #     <h4 style="color: {COLORS["primary"]};">How to Improve Your Resume</h4>
        #     <p>Based on our analysis, here are some suggestions to enhance your resume:</p>
        #     <ul>
        #     <li><strong>Keyword Optimization:</strong> Add more industry-specific keywords that appear in job descriptions you're targeting.</li>
        #     <li><strong>Quantify Achievements:</strong> Add numbers and percentages to demonstrate the impact of your work.</li>
        #     <li><strong>Technical Skills:</strong> Ensure all relevant technical skills are clearly listed in a dedicated section.</li>
        #     <li><strong>Action Verbs:</strong> Start achievement bullets with strong action verbs like "Implemented," "Developed," or "Reduced."</li>
        #     <li><strong>Formatting:</strong> Ensure consistent formatting and eliminate any complex design elements that might confuse ATS systems.</li>
        #     </ul>
        #     </div>
        #     """, unsafe_allow_html=True)
    else:
        # Display a message when no resume is uploaded
        st.markdown(f"""
        <div style="background-color: {COLORS["background"]}; padding: 20px; border-radius: 8px; border: 1px dashed {COLORS["primary"]}; text-align: center; margin-top: 30px;">
        <img src="https://img.icons8.com/fluency/96/000000/resume.png" style="width: 64px; height: 64px; margin-bottom: 15px;">
        <h3 style="color: {COLORS["primary"]};">No Resume Uploaded</h3>
        <p>Upload your resume using the file uploader above to see the analysis.</p>
        </div>
        """, unsafe_allow_html=True)

# Tab 2: Job Search
with tabs[1]:
    st.header("Job Search")
    locations = [
            "Remote",
            "New York, NY", "San Francisco, CA", "Seattle, WA", "Austin, TX",
            "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Atlanta, GA", "Denver, CO",
            "Bangalore, India", "Hyderabad, India", "Mumbai, India", "Delhi, India",
            "Pune, India", "Chennai, India", "London, UK", "Berlin, Germany", "Toronto, Canada"
               ]
    
    # Create search tabs
    search_tabs = st.tabs(["📄 Resume-Based Search", "🔍 Custom Search"])
    
    # Resume-Based Search Tab
    with search_tabs[0]:
        if st.session_state.resume_data:
            st.subheader("Find Jobs Matching Your Resume")
            st.markdown(f"""
            <div style="background-color: {COLORS["panel_bg"]}; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <p style="font-weight: 500; margin-bottom: 10px;">This will extract keywords from your resume and search for relevant jobs automatically.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Extract skills preview from resume
            skills_preview = ", ".join(st.session_state.resume_data.get("skills", [])[:5])
            if skills_preview:
                st.markdown(f"""
                <div style="background-color: {COLORS["secondary"]}; color: white; 
                padding: 10px; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <p style="margin: 0; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                <span style="font-weight: bold;">Top Skills:</span> {skills_preview}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Create two columns for location and search button
            col1, col2 = st.columns([3, 1])
            
            with col1:
                default_location = st.selectbox(
                    "Location:",
                    locations,
                    index=0,
                    key="resume_search_location"
                )
            
            with col2:
                resume_search_button = st.button(
                    "Search Jobs",
                    key="resume_based_search"
                )
            
            if resume_search_button:
                with st.spinner("Extracting key skills and experience from your resume..."):
                    try:
                        # Use the keyword extractor
                        keyword_extractor = resources["keyword_extractor"]
                        search_keywords = keyword_extractor.extract_keywords(st.session_state.resume_data)
                        
                        # Get potential job title
                        job_title = keyword_extractor.extract_job_title(st.session_state.resume_data)
                        
                        # Join with spaces
                        resume_based_query = " ".join(search_keywords)
                        
                        # Display the extracted keywords
                        st.subheader("Extracted Search Terms")
                        
                        # Display with improved contrast
                        st.markdown(f"""
                        <div style="background-color: {COLORS["primary"]}; color: white; 
                        padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <p style="margin-bottom: 8px; font-weight: bold; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                            <span style="font-weight: bold;">Job Title:</span> {job_title.title()}</p>
                            <p style="margin-bottom: 8px; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                            <span style="font-weight: bold;">Keywords:</span> {resume_based_query}</p>
                            <p style="margin-bottom: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                            <span style="font-weight: bold;">Location:</span> {default_location}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Allow user to modify the search terms
                        with st.expander("Modify Search Terms", expanded=False):
                            modified_query = st.text_input("Edit Keywords:", value=resume_based_query)
                            modified_location = st.text_input("Edit Location:", value=default_location)
                            if st.button("Update Search Terms"):
                                resume_based_query = modified_query
                                default_location = modified_location
                                st.success("Search terms updated!")
                        
                        # Search for jobs
                        with st.spinner(f"Searching for jobs matching your resume profile..."):
                            serp_api_searcher = resources["serp_api_searcher"]
                            resume_based_jobs = []
                            
                            # Search on all platforms
                            for platform in JOB_PLATFORMS:
                                try:
                                    platform_jobs = serp_api_searcher.search_jobs(
                                        resume_based_query,
                                        default_location,
                                        platform=platform,
                                        count=5  # Limit to 5 jobs per platform
                                    )
                                    resume_based_jobs.extend(platform_jobs)
                                except Exception as e:
                                    st.error(f"Error searching jobs on {platform}: {str(e)}")
                            
                            # Update job results
                            st.session_state.job_results = resume_based_jobs
                            st.success(f"Found {len(resume_based_jobs)} jobs matching your resume profile!")
                            st.rerun()  # Refresh to show results
                    except Exception as e:
                        st.error(f"Error processing resume data: {str(e)}")
        else:
            st.warning("Please upload your resume in the Resume Analysis tab to enable resume-based job search.")
            
            st.markdown(f"""
            <div style="background-color: {COLORS["panel_bg"]}; padding: 15px; border-radius: 8px;">
            <ol style="margin-left: 15px; margin-bottom: 0;">
            <li>Go to the Resume Analysis tab</li>
            <li>Upload your resume (PDF, DOCX, or TXT)</li>
            <li>Return to this tab to search for jobs based on your resume</li>
            </ol>
            </div>
            """, unsafe_allow_html=True)
    
    # Custom Search Tab
    with search_tabs[1]:
         # Common job titles and locations
        common_job_titles = [
            "Data Scientist", "Software Engineer", "Product Manager", "Data Analyst",
            "Machine Learning Engineer", "Frontend Developer", "Backend Developer",
            "Full Stack Developer", "DevOps Engineer", "UX Designer", "AI Engineer",
            "Cloud Architect", "Database Administrator", "Project Manager", "Business Analyst",
            "Java Developer", "Python Developer", "React Developer", "Android Developer",
            "iOS Developer", "Node.js Developer", "Data Engineer", "Blockchain Developer",
            "Cybersecurity Analyst", "Quality Assurance Engineer"
        ]
    
        locations = [
            "Remote",
            "New York, NY", "San Francisco, CA", "Seattle, WA", "Austin, TX",
            "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Atlanta, GA", "Denver, CO",
            "Bangalore, India", "Hyderabad, India", "Mumbai, India", "Delhi, India",
            "Pune, India", "Chennai, India", "London, UK", "Berlin, Germany", "Toronto, Canada"
               ]
        
        # Job search form
        with st.form("job_search_form"):
            st.subheader("Search Criteria")
            
            # Create a 2-column layout for job title and location
            col1, col2 = st.columns(2)
            
            with col1:
                keywords = st.selectbox("Job Title:", common_job_titles, key="job_titles")
            
            with col2:
                location = st.selectbox("Location:", locations, key="locations")
            
            submit_search = st.form_submit_button("Search Jobs")

            # Execute job search
            if submit_search:
                agent_executor = resources["job_search_agent"]
                input_message = {
                                "role": "user",
                                "content": f"Please search job with the following details:\n\\keywords:\n{keywords}\n\\location:\n{location}"
                            }
                
                try:
                    job_result = agent_executor.invoke({"messages": [input_message]})
                    jobs = clean_jobs_result(job_result)
                    st.session_state.job_results = jobs
                except Exception as e:
                    st.error(f"Error in job search: {e}")
                    st.session_state.job_results = []
                
                st.session_state.job_results = jobs
                print(jobs)
    
    if st.session_state.job_results:
        total_jobs = len(st.session_state.job_results)
        st.subheader(f"Job Results ({total_jobs})")

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            # Sort options
            sort_option = st.selectbox(
                "Sort by:",
                ["Most Recent", "Relevance", "Company Name", "Location"],
                key="sort_option"
                )
        
        with col2:
            # Filter by platform
            filter_platform = st.selectbox(
                "Filter by platform:",
                ["All Platforms"] + JOB_PLATFORMS,
                key="filter_platform"
                )
        
        # Apply platform filter
        filtered_jobs = st.session_state.job_results
        if filter_platform != "All Platforms":
            filtered_jobs = [job for job in filtered_jobs if job.get("platform", "").lower() == filter_platform.lower()]
        
        # st.write(filtered_jobs)

        # Sort jobs based on selection
        sorted_jobs = filtered_jobs.copy()
        if sort_option == "Most Recent":
            # Try to parse dates for sorting
            for job in sorted_jobs:
                if job.get("date_posted") and isinstance(job["date_posted"], str):
                    try:
                        if "hour" in job["date_posted"].lower():
                            hours = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(hours=hours)
                        elif "day" in job["date_posted"].lower():
                            days = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(days=days)
                        elif "week" in job["date_posted"].lower():
                            weeks = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(weeks=weeks)
                        elif "month" in job["date_posted"].lower():
                            months = int(''.join(filter(str.isdigit, job["date_posted"].split()[0])))
                            job["sort_date"] = datetime.now() - timedelta(days=30 * months)
                        else:
                            job["sort_date"] = datetime.now() - timedelta(days=365)
                    except (ValueError, IndexError):
                        job["sort_date"] = datetime.now() - timedelta(days=365)
                else:
                    job["sort_date"] = datetime.now() - timedelta(days=365)
            
            sorted_jobs.sort(key=lambda x: x.get("sort_date"), reverse=False)
        elif sort_option == "Company Name":
            sorted_jobs.sort(key=lambda x: x.get("company", "").lower())
        elif sort_option == "Location":
            sorted_jobs.sort(key=lambda x: x.get("location", "").lower())
        
        if not sorted_jobs:
            st.warning(f"No jobs found for the selected platform: {filter_platform}")
        else:
            # Create a dataframe for easier display
            job_df = pd.DataFrame([
                {
                    "Title": job["title"],
                    "Company": job["company"],
                    "Location": job.get("location", "Not specified"),
                    "Platform": job.get("platform", "Unknown"),
                    "Posted": job.get("date_posted", "Recent"),
                    "Job Type": job.get("job_type", ""),
                    "Real Job": "✓" if job.get("is_real_job", False) else "?"
                }
                for job in sorted_jobs
            ])

            # Display jobs in a dataframe with improved styling
            st.dataframe(
                job_df,
                use_container_width=True,
                column_config={
                    "Title": st.column_config.TextColumn("Job Title"),
                    "Real Job": st.column_config.TextColumn("Verified")
                },
                hide_index=True
            )