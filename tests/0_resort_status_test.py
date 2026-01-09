from crewai import Crew
from agents.agents import resort_status_agent
from agents.tasks import resort_status_task

resort_status_test = Crew(
    name="resort_status_test",
    agents=[resort_status_agent],
    tasks=[resort_status_task],
    sequential=True,
)

result = resort_status_test.kickoff(inputs={"resorts": ["Mammoth Mountain", "Snow Summit"]})
print(result.raw)

# examine output and crosscheck with onthesnow.com for given resorts