from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import asyncio
import httpx
import websockets  # Ensure you run: pip install websockets
import struct
import time

# -----------------------------
# CONFIG
# -----------------------------
BK_IP = "192.168.0.251"
BASE_URL = f"http://{BK_IP}/webxi/applications/slm"
STREAMS_URL = f"http://{BK_IP}/WebXi/Streams"
BK_WS_URL = f"ws://{BK_IP}/WebXi/Streams/1"

# -----------------------------
# SHARED STATE
# -----------------------------
class State:
    def __init__(self):
        self.data = {
            "LAeq": 0.0,
            "status": "init",
            "last_update": 0.0,
            "error": None
        }

state = State()

# -----------------------------
# HARDWARE INITIALIZATION (From Node-RED Flow)
# -----------------------------
async def initialize_hardware(client: httpx.AsyncClient):
    print("Sending setup configurations to Sound Level Meter...")
    
    # 1. Setup sound logging properties
    await client.put(f"{BASE_URL}/Setup", json={
        "ControlLoggingMode": 1,
        "ControlLoggingInterval": 4,
        "ControlMeasurementTimeControl": 0,
        "BBLAeq": True,
        "BBFreqWeightA": True,
        "BBFreqWeightB": False,
        "BBFreqWeightC": False,
        "BBFreqWeightZ": False
    })
    
    # 2. Flush older streams (0 to 21)
    print("Flushing existing stream entries...")
    for i in range(22):
        try:
            await client.delete(f"{STREAMS_URL}/{i}")
        except Exception:
            pass # Ignore if the stream index didn't exist

    # 3. Provision new WebSocket Stream wrapper for Sequence 6 (LAeq)
    print("Provisioning new WebSocket Stream wrapper...")
    await client.post(STREAMS_URL, json={
        "ConnectionType": "WebSocket",
        "Name": "LAeqDNOTA",
        "Sequences": [6],
        "MessageTypes": ["SequenceData"]
    })
    
    # 4. Start recording calculations
    await client.put(f"{BASE_URL}?action=Stop")
    await client.put(f"{BASE_URL}?action=StartPause")
    print("Recording started. Hardware sequence initialized successfully.")

# -----------------------------
# BACKGROUND BINARY WEBSOCKET CLIENT
# -----------------------------
async def bk_websocket_client_task():
    """ Connects to the B&K hardware stream, parses incoming binary data, 
        and populates the shared application state. """
    
    timeout = httpx.Timeout(5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            try:
                # Run the HTTP configuration checklist first
                await initialize_hardware(client)
                state.data["status"] = "connecting"
                
                # Establish client websocket link to the meter stream
                print(f"Connecting to hardware stream: {BK_WS_URL}")
                async with websockets.connect(BK_WS_URL) as ws:
                    print("Core Hardware Stream Link Active.")
                    state.data["status"] = "connected"
                    state.data["error"] = None
                    
                    while True:
                        message = await ws.recv()
                        
                        # Node-RED equivalent checking binary buffer length >= 36 bytes
                        if isinstance(message, bytes) and len(message) >= 36:
                            # Replicating your buffer parsing rules:
                            # Offset 28: SequenceID (Int16, Little Endian)
                            # Offset 30: ValueLength (Int32, Little Endian)
                            # Offset 34: Raw dB value (Int16, Little Endian)
                            sequence_id = struct.unpack_from("<h", message, 28)[0]
                            value_length = struct.unpack_from("<i", message, 30)[0]
                            raw_value = struct.unpack_from("<h", message, 34)[0]
                            
                            # Convert raw data into correct scale decibels (Value / 100)
                            laeq_db = round(raw_value / 100.0, 2)
                            
                            # Update global state reactively
                            state.data["LAeq"] = laeq_db
                            state.data["last_update"] = time.time()
                            
            except Exception as e:
                print(f"Connection or Parsing Error: {e}")
                state.data["status"] = "error"
                state.data["error"] = str(e)
                print("Re-initializing connection pipeline in 5 seconds...")
                await asyncio.sleep(5)

# -----------------------------
# FASTAPI LIFESPAN
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fire up the background listener task immediately when FastAPI launches
    task = asyncio.create_task(bk_websocket_client_task())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

app = FastAPI(lifespan=lifespan)

# -----------------------------
# OUTBOUND FASTAPI WEBSOCKET SERVER
# -----------------------------
@app.websocket("/ws")
async def ws_server_endpoint(websocket: WebSocket):
    """ Server endpoint allowing external dashboard clients to receive 
        real-time LAeq telemetry updates. """
    await websocket.accept()
    
    last_sent_update = 0.0
    try:
        while True:
            # Only send down the pipeline if the hardware state pushed a new metric
            if state.data["last_update"] > last_sent_update or state.data["status"] == "error":
                await websocket.send_json({
                    "LAeq": state.data["LAeq"],
                    "status": state.data["status"],
                    "error": state.data["error"]
                })
                last_sent_update = state.data["last_update"]
                
            # Yield loop briefly to let other asynchronous clients handle execution threads
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
