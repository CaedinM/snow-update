from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime, timezone


## Snowfall Forecasts for upcoming days
class DailySnowfallForecast(BaseModel):
    forecast_date: date = Field(..., description="The date of the forecast")
    forecasted_snow: int = Field(..., description="The forecasted snowfall for the date")

class WeeklySnowfallForecast(BaseModel):
    resort_name: str = Field(..., description="The name of the resort")
    forecast_date: date = Field(default_factory=date.today, description="The date when the forecast was created")
    seven_day_forecast: List[DailySnowfallForecast] = Field(..., description="The forecast for the next 7 days")
    source: str = Field(..., description="The URL of the source of the forecast")


## Resort Status for Current Detailed Information
class ResortStatus(BaseModel): 
    model_config = ConfigDict(extra="forbid")
    resort_name: str = Field(..., description="The name of the resort")
    resort_status: Literal["open", "closed"] = Field(..., description="Whether the resort is currently open for the season or closed")
    base_depth: int = Field(..., description="The depth of the base of the resort in inches")
    summit_depth: int = Field(..., description="The depth of the summit of the resort in inches")
    depth_vs_average: int = Field(..., description="The depth of the base as a percentage of the average depth of the base of the resort on that day of years past")
    lifts_open: int = Field(..., description="The number of lifts that are currently open")
    runs_open: int = Field(..., description="The number of runs that are currently open")
    beginner_runs_open: int = Field(..., description="The number of beginner runs that are currently open")
    intermediate_runs_open: int = Field(..., description="The number of intermediate runs that are currently open")
    advanced_runs_open: int = Field(..., description="The number of advanced runs that are currently open")
    expert_runs_open: int = Field(..., description="The number of expert runs that are currently open")
    open_time: Optional[int] = Field(..., description="The time the resort opens today")
    close_time: Optional[int] = Field(..., description="The time the resort closes today")
    temperature_low: Optional[int] = Field(..., description="The lowest temperature at the resort today in Fahrenheit")
    temperature_high: Optional[int] = Field(..., description="The highest temperature at the resort today in Fahrenheit")
    weekly_snowfall_forecast: WeeklySnowfallForecast = Field(..., description="The forecasted snowfall for the next 7 days")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the data was last updated")

class ResortStatusList(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resorts: List[ResortStatus]


## Daily Message with current conditions and forecast
class DailyUpdateMessage(BaseModel):
    content: str = Field(..., description="The content of the daily update")
    message_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the message was created")