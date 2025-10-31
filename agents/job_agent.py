from langgraph.prebuilt import create_react_agent
# from tools.analysize_jobs_tool import return_job_match_tool
from tools.job_search_tool import job_search_tool
from tools.resume_analysis_tool import analyze_resume

## error : llm not found

def get_job_search_agent(llm):
    # job_match_tool = return_job_match_tool()
    agent_executor = create_react_agent(llm, [analyze_resume,job_search_tool])

    return agent_executor