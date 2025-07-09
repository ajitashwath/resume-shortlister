from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import PDFSearchTool
from src.resume_shortlisting.tools.custom_tool import ExtractResumeText
import yaml
from pathlib import Path
import os

@CrewBase
class ResumeShortlistingCrew(): 
    def __init__(self, api_key=None):
        self.agents_config = self._load_config('config/agents.yaml')
        self.tasks_config = self._load_config('config/tasks.yaml')
        self.api_key = api_key
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key

    def _load_config(self, file_path: str) -> dict:
        module_dir = Path(__file__).parent
        config_path = module_dir / file_path
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    @agent
    def jd_interpreter(self) -> Agent:
        config = self.agents_config['jd_interpreter']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=True,
            llm_config={    #type: ignore
                "model": "gpt-4o-mini",
                "api_key": self.api_key
            } if self.api_key else None
        )

    @agent
    def resume_analyst(self) -> Agent:
        config = self.agents_config['resume_analyst']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=True,
            tools=[ExtractResumeText()],
            llm_config={    #type: ignore
                "model": "gpt-4o-mini",
                "api_key": self.api_key
            } if self.api_key else None
        )

    @task
    def analyze_jd(self) -> Task:
        config = self.tasks_config['analyze_jd']
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.jd_interpreter()
        )

    @task
    def shortlist_resumes(self) -> Task:
        config = self.tasks_config['shortlist_resumes']
        return Task(
            description=config['description'],
            expected_output=config['expected_output'],
            agent=self.resume_analyst(),
            context=[self.analyze_jd()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.jd_interpreter(), self.resume_analyst()],
            tasks=[self.analyze_jd(), self.shortlist_resumes()],
            process=Process.sequential,
            verbose=True,
        )