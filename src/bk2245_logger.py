import asyncio
import requests
import urllib3
from fastapi import FastAPI, WebSocket
from datetime import datetime

<<<<<<< HEAD
urllib3.disable_warnings()

app = FastAPI()

BK_URL = "https://IP_SONOMETER/webxi/Applications/SLM/Output"

latest_measurement = {
    "timestamp": None,
    "LFA": None
}
=======
LOGFILE = "/home/pi/bk2245-logger/data/bk2245.csv"
API_PATH = "webxi/Applications/SLM/Outputs"
TIMEOUT = 0.5
>>>>>>> 6233ab5ce21a0d0f4283d3e01d3a2833ca57f570


# ------------------------
# Poll B&K every 5 seconds
# ------------------------
async def poll_bk():
    global latest_measurement

    while True:
        try:
            response = requests.get(
                BK_URL,
                verify=False,
                timeout=3
            )

            data = response.json()

            # Adjust this path if JSON differs
            latest_measurement = {
                "timestamp": datetime.utcnow().isoformat(),
                "LFA": data.get("LFA")
            }

            print(latest_measurement)

        except Exception as e:
            print("B&K error:", e)

        await asyncio.sleep(5)


# ------------------------
# Startup background task
# ------------------------
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(poll_bk())


<<<<<<< HEAD
# ------------------------
# HTTP endpoint
# ------------------------
@app.get("/")
def root():
    return latest_measurement
=======
def save(data):
    file_exists = Path(LOGFILE).exists()

    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "laf": data.get("LAF"),
        "laeq": data.get("LAeq"),
        "lmax": data.get("Lmax"),
        "lpeak": data.get("LPeak"),
    }

    with open(LOGFILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)
>>>>>>> 6233ab5ce21a0d0f4283d3e01d3a2833ca57f570


# ------------------------
# WebSocket endpoint
# ------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

<<<<<<< HEAD
    while True:
        await websocket.send_json(latest_measurement)
        await asyncio.sleep(5)
=======
    if not ip:
        print("B&K not found")
        return

    data = get_measurement(ip)
    save(data)

    print(f"Logged data from {ip}")


if __name__ == "__main__":
    main()
>>>>>>> 6233ab5ce21a0d0f4283d3e01d3a2833ca57f570
