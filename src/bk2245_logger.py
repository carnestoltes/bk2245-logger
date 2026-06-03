from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import asyncio
import httpx
import time

# -----------------------------
# CONFIG
# -----------------------------

BK_IP = "192.168.0.251"
BK_Time = f"http://{BK_IP}/webxi/Applications/SLM/Outputs/StartTime"
BK_LAF = f"http://{BK_IP}/webxi/Applications/SLM/Outputs/LAF"

POLL_INTERVAL = 5

# -----------------------------
# SHARED STATE (NO GLOBALS HACKING)
# -----------------------------
class State:
    def __init__(self):
        self.data = {
            "Time": None,
            "LAF": None,
            "status": "init",
            "last_update": None,
            "errors": []
        }

state = State()

# -----------------------------
# FASTAPI LIFESPAN
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(poll_bk())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except:
            pass


app = FastAPI(lifespan=lifespan)

# -----------------------------
# ASYNC POLLING ENGINE
# -----------------------------
async def poll_bk():
    timeout = httpx.Timeout(3.0)

    async with httpx.AsyncClient(timeout=timeout) as client:

        while True:
            try:
                # parallel requests (important improvement)
                time_req = client.get(BK_Time)
                laf_req = client.get(BK_LAF)
                
                time_resp, laf_resp  = await asyncio.gather(time_req, laf_req)

                time_resp.raise_for_status()
                laf_resp.raise_for_status()
                
                state.data["Time"] = time_resp.text.strip()
                state.data["LAF"] = laf_resp.text.strip()
                
                state.data["status"] = "ok"
                state.data["last_update"] = time.time()

            except Exception as e:
                state.data["status"] = "error"
                state.data["errors"].append(str(e))

            await asyncio.sleep(POLL_INTERVAL)


# -----------------------------
# REST ENDPOINT
# -----------------------------
@app.get("/")
async def root():
    return state.data


# -----------------------------
# WEBSOCKET STREAM
# -----------------------------
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            await websocket.send_json(state.data)
            await asyncio.sleep(1)

    except Exception:
        pass
