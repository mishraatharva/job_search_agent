# create file here : 

mkdir -p job_search_assistant/{agents,utils}

touch job_search_assistant/{app.py,config.py,requirements.txt}
touch job_search_assistant/agents/{__init__.py,resume_agent.py,job_search_agent.py,interview_agent.py}
touch job_search_assistant/utils/{__init__.py,resume_parser.py,job_scraper.py}




 # install this also here 

pip install spacy
python -m spacy download en_core_web_lg
