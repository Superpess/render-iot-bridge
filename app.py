import os
from fastapi import FastAPI
from datetime import datetime
import pytz

app = FastAPI()

@app.get("/health")
def health():
    print("HEALTH CALLED")
    return {"status": "ok"}


@app.get("/time")
def time_now():
    tz = pytz.timezone("Europe/Rome")
    return {"rome_time": datetime.now(tz).isoformat()}

# Endpoint finto per simulare l'API irrigazione (senza software cliente)
@app.get("/api/v1/site/{site_id}/sensors/latest")
def latest(site_id: str):
    return {
        "site_id": site_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "soil_moisture": 23.4,
        "soil_temp": 14.8,
        "rain_daily": 0.0,
        "air_temp": 12.3,
        "air_rh": 71.0
    }
