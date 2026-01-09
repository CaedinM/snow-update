from crewai import Crew
from agents.agents import resort_status_agent, daily_update_agent
from agents.tasks import resort_status_task, daily_update_task

daily_update_test_crew = Crew(
    name="daily_update_test_crew",
    agents=[resort_status_agent, daily_update_agent],
    tasks=[resort_status_task, daily_update_task],
    sequential=True,
)

result = daily_update_test_crew.kickoff(inputs={"resorts": ["Mammoth Mountain", "Snow Summit"]})
print(result.raw)