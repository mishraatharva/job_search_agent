from langchain_core.tools import tool
from config import JOB_PLATFORMS
from utils.job_scraper import JobScraper
from utils.serp_api_searcher import SerpApiSearcher

@tool
def job_search_tool(resume_data, keywords, location, platforms=None, count=5):
        """
        Search for jobs based on resume and keywords.
        
        Args:
            resume_data (dict): The parsed resume data
            keywords (str): Search keywords or job title
            location (str): Job location
            platforms (list): List of job platforms to search
            count (int): Number of jobs per platform
            
        Returns:
            list: List of job dictionaries
        """
        print("------------------------------------------------------")
        print("inside job_search_tool")
        print("-------------------------------------------------------")
        
        job_scraper = JobScraper()
        serp_api_searcher = SerpApiSearcher()

        if not platforms:
            platforms = JOB_PLATFORMS
            
        # Try the SerpAPI approach first (this will have real links)
        api_jobs = []
        
        # for platform in platforms:
        #     # Use SerpAPI to search for real jobs
        #     platform_jobs = serp_api_searcher.search_jobs(
        #         keywords, 
        #         location, 
        #         platform=platform, 
        #         count=count
        #     )
        #     api_jobs.extend(platform_jobs)
        
        # # If we got results from SerpAPI, use those
        # if api_jobs:
        #     return api_jobs
        
        # Fallback to the scraper if SerpAPI fails
        print("SerpAPI search returned no results. Falling back to scraper.")
        all_jobs = []
        for platform in platforms:
            platform_jobs = job_scraper.search_jobs(
                keywords, 
                location, 
                platform=platform, 
                count=count
            )
            all_jobs.extend(platform_jobs)
        
        return all_jobs