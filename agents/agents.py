from crewai import Agent, LLM
from .tools import scrape_tool
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = llm = LLM(model="gpt-4o", api_key=OPENAI_API_KEY)


resort_status_agent = Agent(
    role="Resort Status Researcher",
    goal="Check the current status of ski resorts and gather accurate information about snow conditions, lift operations, and resort status",
    backstory="""You are an expert researcher specializing in ski resort conditions. 
    You know that search results only show snippets - to get complete information, you must:
    1. Use search to find the exact skireport URL for each resort
    2. Scrape the full page content from that URL to extract all details
    3. Parse the page carefully to find all required fields (lifts, runs, snow depth, temperatures, etc.)
    Always scrape the full page - don't rely on search snippets alone.""",
    tools=[scrape_tool],
    verbose=True,
    allow_delegation=False,
)

daily_update_agent = Agent(
    role="Daily Update Agent",
    goal="""Provide a daily update to skiers about the status of ski resorts and the forecasted 
    snowfall for the next 7 days""",
    backstory="""You are a helpful assistant that writes messages to update
    skiers about the current and upcoming status and conditions of ski resorts.
    You talk in a cool and casual tone.""",
    tools=[],
    verbose=True,
    allow_delegation=False,
)

snowfall_alert_agent = Agent(
    role="Snowfall Alert Coordinator",
    goal="Monitor resort status information and provide timely alerts and daily updates to skiers about upcoming snowfall",
    backstory="You are a helpful assistant that monitors resort conditions and provides clear, actionable updates to skiers about snowfall forecasts and resort status.",
    tools=[],
    verbose=True,
    allow_delegation=False,
)
