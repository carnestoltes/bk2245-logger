import asyncio
import socket
import requests
import urllib3
import subprocess
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from datetime import datetime

urllib3.disable_warnings()

BK_IP = "192.168.0.251"
BK_URL = f"https://{BK_IP}/webxi/Applications/SLM/Output"

latest_measurement = {
    "timestamp": None,
    "LFA": None
}


async def wait_for_usb0():

    print("Waiting for usb0...")

    while True:
        try:
            result = subprocess.run(
                ["ip", "addr", "show", "usb0"],
                capture_output=True,
                text=True
            )

            if "inet " in result.stdout:
                print("usb0 ready")
                return

        except Exception as e:
            print("usb0 check error:", e)

        await asyncio.sleep(2)


async def wait_for_bk():

    print("Waiting for B&K...")

    while True:
        try:
            requests.get(
                BK_URL,
                verify=False,
                timeout=3
            )

            print("B&K reachable")
            return

        except Exception:
            pass

        await asyncio.sleep(2)


async def poll_bk():
    global latest_measurement

    await wait_for_usb0()
    await wait_for_bk()

    while True:
        try:
            response = requests.get(
                BK_URL,
                verify=False,
                timeout=3
            )

            data = response.json()

            latest_measurement = {
                "timestamp": datetime.utcnow().isoformat(),
                "LFA": data.get("LFA")
            }

            print(latest_measurement)

        except Exception as e:
            print("B&K error:", e)

        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):

    task = asyncio.create_task(poll_bk())

    yield

    task.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return latest_measurement


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    while True:
        await websocket.send_json(latest_measurement)
        await asyncio.sleep(5)