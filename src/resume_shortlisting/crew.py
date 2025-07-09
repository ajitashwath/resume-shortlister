from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import PDFSearchTool
from src.resume_shortlisting.tools.custom_tool import ExtractResumeText
from langchain_openai import ChatOpenAI

@CrewBase
class ResumeShortlistingCrew(): 
    def __init__(self, api_key=None):
        self.agents_config = self.load_agents_config()
        self.tasks_config = self.load_tasks_config()
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=api_key
        )
    
    def load_agents_config(self):
        return {
            'jd_interpreter': {
                'role': 'Job Description Analyst',
                'goal': 'Extract key requirements, skills, and qualifications from job descriptions to enable precise candidate evaluation.',
                'backstory': 'You are a strategic HR professional with years of experience writing and interpreting job descriptions. You specialize in breaking down complex job postings into actionable hiring criteria to support effective recruitment decisions. Your analysis helps recruitment teams focus on what really matters for hiring success.'
            },
            'resume_analyst': {
                'role': 'Resume Screener',
                'goal': 'Evaluate and rank resumes based on alignment with job requirements.',
                'backstory': 'You are a recruitment expert trained in analyzing resumes with precision. You identify strengths, weaknesses, and red flags in candidate applications, using clear evaluation frameworks. Your insights directly impact hiring outcomes by shortlisting the most qualified candidates for the role.'
            }
        }
    
    def load_tasks_config(self):
        return {
            'analyze_jd': {
                'description': 'Carefully analyze the provided job description: {job_description}. Your goal is to summarize the most important requirements the hiring manager is looking for. Break down the description into must-have skills, nice-to-have skills, required experience, and relevant industries.',
                'expected_output': 'A structured summary including: - List of must-have skills and qualifications - List of nice-to-have skills - Required years of experience - Preferred industries or domains'
            },
            'shortlist_resumes': {
                'description': 'Based on the job requirements analysis, analyze the set of resumes provided: {resumes}. Rank them for fit and evaluate each resume on a scale from 1 to 10. For each candidate, extract their name, mobile number, and generate 2-3 specific interview questions based on their background and the job requirements.',
                'expected_output': 'A structured table with columns: Name, Mobile, Score, Questions for Interview. Include only the top candidates with scores above 7.'
            }
        }

    @agent
    def jd_interpreter(self) -> Agent:
        config = self.agents_config['jd_interpreter']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def resume_analyst(self) -> Agent:
        config = self.agents_config['resume_analyst']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            llm=self.llm,
            verbose=True,
            tools=[ExtractResumeText()]
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