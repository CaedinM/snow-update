from crewai import Crew
from .agents import resort_status_agent, snowfall_alert_agent
from .tasks import resort_status_task, snowfall_alert_task

snow_update_crew = Crew(
    name="snow_update_crew",
    agents=[resort_status_agent, snowfall_alert_agent],
    tasks=[resort_status_task, snowfall_alert_task],
    sequential=True,
)

