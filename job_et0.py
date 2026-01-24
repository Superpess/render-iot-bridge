import os
import requests
from datetime import datetime
import pytz
import time
import random

TB_HOST = os.environ.get("TB_HOST", "https://thingsboard.cloud").rstrip("/")
TB_DEVICE_TOKEN = os.environ["TB_DEVICE_TOKEN"]
LAT = float(os.environ["LAT"])
LON = float(os.environ["LON"])
ET0_KEY = os.environ.get("ET0_KEY", "et0")

def fetch_openmeteo_et0_daily(lat, lon, timezone="Europe/Rome", max_retries=6):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "et0_fao_evapotranspiration",
        "timezone": timezone
    }

    for attempt in range(max_retries):
        r = requests.get(url, params=params, timeout=30)

        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                sleep_s = int(retry_after)
            else:
                sleep_s = min(300, (2 ** attempt)) + random.uniform(0, 1.0)
            print(f"Open-Meteo 429: attendo {sleep_s:.1f}s e ritento ({attempt+1}/{max_retries})")
            time.sleep(sleep_s)
            continue

        r.raise_for_status()
        data = r.json()

        et0_list = data.get("daily", {}).get("et0_fao_evapotranspiration", [])
        if not et0_list:
            raise RuntimeError("Risposta Open-Meteo senza et0_fao_evapotranspiration")

        return float(et0_list[0])

    raise RuntimeError("Open-Meteo: troppi 429 consecutivi")


def send_to_thingsboard(et0_value: float):
    url = f"{TB_HOST}/api/v1/{TB_DEVICE_TOKEN}/telemetry"
    payload = {ET0_KEY: et0_value}
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()


def main():
    try:
        # Ritardo anti-429
        delay = random.randint(10, 120)
        print(f"Delay anti-429: {delay}s")
        time.sleep(delay)

        # TEST: ET0 forzato a 0
        et0 = 0
        print("TEST MODE: ET0 forzato a 0")

        # Invio a ThingsBoard
        send_to_thingsboard(et0)

        now_rome = datetime.now(pytz.timezone("Europe/Rome")).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[OK] {now_rome} - sent {ET0_KEY}={et0} to ThingsBoard")

    except Exception as e:
        print(f"[WARN] ET0 job error (non blocking): {e}")
        return





if __name__ == "__main__":
    main()
