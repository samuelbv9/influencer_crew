from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from langchain_openai import ChatOpenAI

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class InfluencerCrew():
	"""InfluencerCrew crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def alignment_evaluator(self) -> Agent:
		return Agent(
			config=self.agents_config['alignment_evaluator'],
			tools=[],
			verbose=True
		)
	
	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task

	@task
	def alignment_evaluation_task(self) -> Task:
		return Task(
			config=self.tasks_config['alignment_evaluation_task'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the InfluencerCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		# Read the content of the knowledge file
		with open("knowledge/stir_info.txt", "r") as file:
			stir_info_content = file.read()

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			# process=Process.hierarchical,  # Use hierarchical process
			process=Process.sequential,
			verbose=True,
			# manager_llm=ChatOpenAI(temperature=0, model="gpt-4o-mini"),
			# planning=True,  # Enable planning feature for pre-execution strategy
			knowledge_sources=[
            	StringKnowledgeSource(
                	content=stir_info_content,
                	metadata={"source": "stir_info.txt"}  # Add non-empty metadata
            	)
        	]
		)
