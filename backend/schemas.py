from pydantic import BaseModel, ConfigDict, Field, BeforeValidator
from typing import Annotated
from bson import ObjectId

def oid_to_str(v: any) -> any:
    if isinstance(v, ObjectId):
        return str(v)
    return v

OidStr = Annotated[str, BeforeValidator(oid_to_str)]

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: OidStr = Field(alias="_id")
    username: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class SchemeBase(BaseModel):
    title: str
    summary: str | None = None
    url: str
    created_at: str
    updated_at: str

class Scheme(SchemeBase):
    pass

class SchemePage(BaseModel):
    id: OidStr = Field(alias="_id")
    title: str
    summary: str | None = None
    schemes: list[Scheme] = []
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class PredictionResponse(BaseModel):
    status: str
    confidence: str
    message: str | None = None
    crop_name: str | None = None
    disease_name: str | None = None
    scientific_name: str | None = None
    symptoms: list[str] | None = None
    treatment: list[str] | None = None
    recommendations: list[str] | None = None
    precautions: list[str] | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class WeatherConditionDescription(BaseModel):
    text: str
    languageCode: str

class WeatherCondition(BaseModel):
    iconBaseUri: str
    description: WeatherConditionDescription
    type: str

class Temperature(BaseModel):
    degrees: float
    unit: str

class WindSpeed(BaseModel):
    value: float
    unit: str

class WindDirection(BaseModel):
    degrees: int
    cardinal: str

class Wind(BaseModel):
    direction: WindDirection
    speed: WindSpeed
    gust: WindSpeed

class PrecipitationQuantity(BaseModel):
    quantity: float
    unit: str

class PrecipitationProbability(BaseModel):
    percent: int
    type: str

class Precipitation(BaseModel):
    probability: PrecipitationProbability
    snowQpf: PrecipitationQuantity
    qpf: PrecipitationQuantity

class DayNightForecast(BaseModel):
    weatherCondition: WeatherCondition
    relativeHumidity: int
    uvIndex: int
    precipitation: Precipitation
    thunderstormProbability: int
    wind: Wind
    cloudCover: int

class SunEvents(BaseModel):
    sunriseTime: str
    sunsetTime: str

class MoonEvents(BaseModel):
    moonPhase: str
    moonriseTimes: list[str] | None = None
    moonsetTimes: list[str] | None = None

class DisplayDate(BaseModel):
    year: int
    month: int
    day: int

class DailyForecast(BaseModel):
    displayDate: DisplayDate
    daytimeForecast: DayNightForecast
    nighttimeForecast: DayNightForecast
    maxTemperature: Temperature
    minTemperature: Temperature
    sunEvents: SunEvents
    moonEvents: MoonEvents

class TimeZone(BaseModel):
    id: str

class WeatherResponse(BaseModel):
    forecastDays: list[DailyForecast]
    timeZone: TimeZone

class HourlyForecast(BaseModel):
    time: str
    temperature: Temperature
    weatherCondition: WeatherCondition
    precipitation: Precipitation
    relativeHumidity: int
    wind: Wind

class HourlyWeatherResponse(BaseModel):
    hourlyForecasts: list[HourlyForecast]

class SprayingCondition(BaseModel):
    time: str
    condition: str  
    wind_kph: float
    temperature_c: float
    precipitation_chance: int
    humidity: int
    reason: str

class SprayingConditionsResponse(BaseModel):
    conditions: list[SprayingCondition]
