from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# from tools.CalenderTool import CustomCalenderTool
from langchain_community.tools import DuckDuckGoSearchRun

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


@CrewBase
class backendcrewCrew:
    """Backendcrew crew setup"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        # Initialize the LLM with specific settings
        # self.llm = ChatGroq(model_name="llama-3.1-70b-versatile")  # llama-3.1-8b-instant
        self.llm = "groq/llama-3.1-70b-versatile"

    # @agent
    # def notebook_resource_manager(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['notebook_resource_manager'],
    #         llm=self.llm,
    #         verbose=True
    #     )
    #
    # @agent
    # def schedule_agent(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['schedule_agent'],
    #         tools=[CustomCalenderTool()],
    #         llm=self.llm,
    #         verbose=True
    #     )
    #
    # @agent
    # def performance_analyst(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['performance_analyst'],
    #         llm=self.llm,
    #         verbose=True
    #     )

    # @agent # Don't include in the crew
    def manager_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['manager_agent'],
            llm=self.llm,
            verbose=True
        )

    @agent
    def misc_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['misc_agent'],
            tools=[DuckDuckGoSearchRun()],  # Web search tool for handling general queries
            llm=self.llm,
            verbose=True
        )

    @task
    def route_query(self) -> Task:
        return Task(
            config=self.tasks_config['route_query_task'],
        )

    # @task
    # def organize_resources(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['organize_resources_task'],
    #     )
    #
    # @task
    # def create_study_schedule(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['create_study_schedule_task'],
    #     )
    #
    # @task
    # def analyze_performance(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['analyze_performance_task'],
    #     )

    @task
    def handle_misc_queries(self) -> Task:
        return Task(
            config=self.tasks_config['miscellaneous_task_handling'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StudyTracker crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.hierarchical,
            manager_agent=self.manager_agent(),
            manager_llm=self.llm,
            verbose=False,

        )


if __name__ == '__main__':
    crew = backendcrewCrew().crew()
    response = crew.kickoff(inputs={'query': input("Query:")})
    # response = crew.manager_agent.execute_task(crew.tasks[0], context=input("Query:"))
    print(f"\n\n{response.raw=}")
