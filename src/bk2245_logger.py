import asyncio
import requests
import urllib3
from fastapi import FastAPI, WebSocket
from datetime import datetime

urllib3.disable_warnings()

app = FastAPI()

BK_URL = "https://IP_SONOMETER/webxi/Applications/SLM/Output"

latest_measurement = {
    "timestamp": None,
    "LFA": None
}



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


# ------------------------
# HTTP endpoint
# ------------------------
@app.get("/")
def root():
    return latest_measurement

# ------------------------
# WebSocket endpoint
# ------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        await websocket.send_json(latest_measurement)
        await asyncio.sleep(5)



