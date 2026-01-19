import os
import requests
from datetime import datetime
import pytz

TB_HOST = os.environ.get("TB_HOST", "https://thingsboard.cloud").rstrip("/")
TB_DEVICE_TOKEN = os.environ["TB_DEVICE_TOKEN"]
LAT = float(os.environ["LAT"])
LON = float(os.environ["LON"])
ET0_KEY = os.environ.get("ET0_KEY", "et0")

def fetch_openmeteo_et0_daily(lat: float, lon: float) -> float:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=et0_fao_evapotranspiration"
        "&timezone=Europe%2FRome"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    vals = data.get("daily", {}).get("et0_fao_evapotranspiration", [])
    if not vals:
        raise RuntimeError("Open-Meteo: daily.et0_fao_evapotranspiration vuoto/non presente")
    return float(vals[0])

def send_to_thingsboard(et0_value: float):
    url = f"{TB_HOST}/api/v1/{TB_DEVICE_TOKEN}/telemetry"
    payload = {ET0_KEY: et0_value}
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()

def main():
    tz = pytz.timezone("Europe/Rome")
    now_rome = datetime.now(tz).isoformat()
    et0 = fetch_openmeteo_et0_daily(LAT, LON)
    send_to_thingsboard(et0)
    print(f"[OK] {now_rome} - sent {ET0_KEY}={et0} to ThingsBoard")

if __name__ == "__main__":
    main()
