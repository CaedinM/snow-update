import os
from crewai_tools import TavilySearchTool, ScrapeWebsiteTool

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

search_tool = TavilySearchTool()

scrape_tool = ScrapeWebsiteTool()
