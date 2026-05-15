# B&K 2245 Raspberry Pi Logger & WebSocket Gateway

This project collects measurement data from a Brüel & Kjær 2245 sound level meter via its HTTP (WebXi) API using a Raspberry Pi.  
It stores data locally and optionally exposes it in real time using a WebSocket server.

---

## Features

- Auto-detects B&K device over USB Ethernet
- Reads measurement via HTTP API
- Real-time WebSocket streaming
- Works with systemd service (auto-start on boot)
- Supports NAT/port forwarding for remote access

---

## Requirements

- Raspberry Pi (tested on Pi 2B)
- Python 3
- Internet / local network access to B&K 2245

Install dependencies:

```bash
sudo apt update
pip3 install fastapi uvicorn requests
pip3 install -r requirements.txt
```
## Installation

```bash
git clone https://github.com/carnestoltes/bk2245-logger.git
cd bk2245-logger
```
```bash
sudo cp systemd/bk2245.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bk2245.service
sudo systemctl start bk2245.service
```
## Debug

```bash
journalctl -u bk2245.service -f
```

## Run Locally

```bash
uvicorn app:app --host 0.0.0.0 --port 5003
```

## WebSocket Test

```bash
npm install -g wscat
wscat -c ws://IP_sonometer/ws
```

## WebSocket Test NAT

```bash
http://PUBLIC_IP:5003
ws://your-domain:5003/ws
```