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
BK_Time = f"https://{BK_IP}/webxi/Applications/SLM/Outputs/StartTime"
BK_LFA = f"https://{BK_IP}/webxi/Applications/SLM/Outputs/LFA"

latest_measurement = {
    "timestamp": None,
    "LFA": None
}


#async def configure_usb0():

 #   IP = "192.168.0.253/24"

  #  print("Waiting for usb0...")

   # while True:
    #    try:
     #       result = await asyncio.to_thread(
      #          subprocess.run,
       #         ["ip", "addr", "show", "usb0"],
        #        capture_output=True,
         #       text=True
          #  )

            # Interface exists
           # if result.returncode == 0:

            #    print("usb0 detected")

                # Bring interface up
             #   await asyncio.to_thread(
              #      subprocess.run,
               #     ["sudo", "ip", "link", "set", "usb0", "up"],
                #    check=True
                #)

                # Assign IP
                #await asyncio.to_thread(
                 #   subprocess.run,
                  #  [
                   #     "sudo",
                    #    "ip",
                     #   "addr",
                      #  "add",
                       # IP,
                        #"dev",
                        #"usb0"
                    #],
                    #check=False
                #)

                #print(f"Assigned {IP} to usb0")

                #return

        #except Exception as e:
         #   print("usb0 config error:", e)

        #await asyncio.sleep(2)
async def poll_bk():
    global latest_measurement

    #await configure_usb0()
    #await wait_for_bk()
    
    while True:
        try:
            r1 = requests.get(BK_Time, timeout=3)
            latest_measurement["timestamp"] = r1.text.strip()

            r2 = requests.get(BK_LFA, timeout=3)
            latest_measurement["LFA"] = r2.text.strip()

        except Exception as e:
            latest_measurement["error"] = str(e)

        await asyncio.sleep(5)


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


@app.get("/")
def root():
    return latest_measurement


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    try:
        while True:
            await websocket.send_json(latest_measurement)
            await asyncio.sleep(5)

    except Exception:
        # client disconnected or error
        pass
