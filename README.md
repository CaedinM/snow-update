# AI Snow Conditions Update System

## Overview:
This project provides an AI-powered system for delivering up-to-date snow and resort conditions for ski resorts. It scrapes data from onthesnow.com to provide detailed daily information about each resort such as current status, snow depth, open lifts and runs, temperatures, and 7-day snowfall forecasts. It generates and delivers daily updates and snowfall notifications straight to the user via text message, making it easy to stay informed about ski conditions and make timely decisions for your next trip to the slopes.

## Tech Stack:
- **Crew AI**: AI agents
- **Streamlit**: minimal frontend for sign-up

## Prerequisites and local setup
1. **Python 3.9+**  
2. **pip (Python package manager)**  

3. **Install Requirements**  
   ```bash
   pip install -r requirements.txt
   ```

5. **API Keys**  
    - project uses OpenAI API for llms
    - project uses Tavily for agent search tool

   create a `.env` file at the project root and add your `OPENAI_API_KEY` and `TAVILY_API_KEY`

6. **Internet Access**  
   The application scrapes data from onthesnow.com, so make sure your environment has internet access.

7. **(Optional) SMS/Notification Service Setup**  
   If you want to receive snow updates via text message or other notifications, you'll need to configure the necessary service (e.g., Twilio) and set related credentials.

Once prerequisites are met, follow the usage instructions to run the project.

## Testing:
Local tests are provided to test LLM system
```bash
# Test the resort_status_agent and resort_status_task
python -m tests.0_resort_status_test

# Test the full crew with message generation
python -m tests.1_daily_update_test
```

One day Build by:  
Caedin Manners  
caedinmanners@berkeley.edu