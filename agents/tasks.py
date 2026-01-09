from .agents import resort_status_agent, daily_update_agent, snowfall_alert_agent
from .models import ResortStatusList, DailyUpdateMessage
from .tools import search_tool, scrape_tool
from crewai import Task

resort_status_task = Task(
    name="resort_status_task",
    description="""
    Search https://www.onthesnow.com/ to find the latest information about the conditions and status of the following ski resorts: {resorts}.

    The skireport URLs follow this pattern:
    - Bear Mountain: https://www.onthesnow.com/california/bear-mountain/skireport
    - Snow Summit: https://www.onthesnow.com/california/snow-summit/skireport
    Use onthesnow.com as your primary source. All of the information you need is there.
    WORKFLOW:
    1. Search for each resort's skireport page
    2. Scrape the FULL page content from the skireport URL
    3. Extract all information from the scraped HTML content
    
    notes:
    - "lifts open: 3/7" indicates that total_lifts=7 and open_lifts=3.
    - The same goes for runs: "Runs open: 5/26" indicates total_runs=26 and open_runs=5.
    - Do not confuse recent snowfall values with the snow forecast. The snow forecast is under forecasted snow. 
    Consider what day of the week it is today if you have to. The first value in the forecasted snow is today followed
    by upcoming days.
    """,
    expected_output="""
    Full information about the status of the resort and snow conditions, including the number of lifts open, the number of runs open, the snow depth, the temperature, and the base conditions, etc.

    OUTPUT CONTRACT (STRICT):
    - Return ONLY a single ResortStatusList Pydantic object.
    - DO NOT add additional fields that are not outlined in the Pydantic model.
    - Do NOT wrap in markdown.
    - Do NOT include any commentary.
    - Types must be correct (numbers are numbers, null is null).
    - If a field is unknown, use null (not "unknown").
    """,
    output_pydantic=ResortStatusList,
    agent=resort_status_agent,
    tools=[search_tool, scrape_tool],
)

daily_update_task = Task(
    name="daily_update_task",
    description="""
    Addressing the user like a friend, write a short message updating them about the current conditions at {resorts}.
    Use a friendly and engaging tone.
    """,
    expected_output="""
    return a DailyUpdateMessage Pydantic object.
    the message field should be a your own written message string.

    Format:
    - Start the message with a short greeting and summary of the current conditions 
    and upcoming snowfall forecast. If anything stands out in the data, mention it (ex: upcoming
    snowfall after dry spell, sustained snowfall, unusually warm or cold temperatures, etc.).
    -Then List the key datapoints for each resort in {resorts}.

    Example message for inputs: resorts = Bear Mountain, Mammoth Mountain:
    Good morning legend! Here's your <date> update for Bear Mountain and Mammoth Mountain:
    No snowfall expected at Bear Mountain but Mammoth is going strong with 62" of depth at the 
    base and 94" at the summit. No more snowfall expected in the coming week so get up there and enjoy it
    before it melts away!

    Today's Info:
    <resort_name>: <status> (if status is closed, say what time it opens today. If you don't know, just say "closed")
    - ◻️ Base Depth: <base_depth> inches
    - 🏔️ Summit Depth: <summit_depth> inches
    - 🚡 Lifts Open: <lifts_open> / <lifts_total>
    - 🎿 Runs Open: <runs_open> / <runs_total>
    - 🌨️ Snowfall Forecast: give a verbal summary of how much snow is expected to fall over the next 7 days. Keep it brief, one sentence max.
    Full Info: <source_url>

    repeat for all resorts in {resorts}...

    - DO NOT include information that is not in the ResortStatusList object.
    """,
    context=[resort_status_task],
    output_pydantic=DailyUpdateMessage,
    agent=daily_update_agent,
)