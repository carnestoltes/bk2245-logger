# Edge IoT Gateway: B&K 2245 Raspberry Pi Logger & WebSocket Streamer

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async%20API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Edge%20Device-C51A4A?logo=raspberrypi&logoColor=white)](https://www.raspberrypi.com/)
[![Linux](https://img.shields.io/badge/Linux-Systemd%20Service-F29111?logo=linux&logoColor=white)](https://systemd.io/)

---

## What it does

This project turns a **Raspberry Pi into an edge IoT gateway** that interfaces with a **Brüel & Kjær 2245 Sound Level Meter** — a professional-grade acoustic measurement instrument — and streams its telemetry data in real time over WebSocket.

The meter exposes measurements through its built-in WebXi HTTP API over a USB Ethernet-over-USB (CDC ECM/RNDIS) interface. This service polls that API continuously, manages the USB network interface automatically, and re-broadcasts the data to any number of connected clients (dashboards, monitoring tools, cloud pipelines) via WebSocket.

**Use case:** Automated acoustic monitoring in industrial or environmental settings, where legacy instruments need to feed data into modern IoT pipelines without manual intervention.

```
B&K 2245 Meter ──USB (usb0)──► Raspberry Pi ──WebSocket /ws──► Dashboards / Cloud
                                     │
                              Systemd service
                           (auto-start, self-healing)
```

---

## Key architectural features

- **Virtual network interface (USB CDC ECM/RNDIS):** manages the `usb0` Ethernet-over-USB link between meter and Pi automatically
- **Async data pipeline:** FastAPI + HTTPX for non-blocking polling and concurrent broadcasting
- **Self-healing via Systemd:** auto-starts on boot, recovers from crashes, rotates logs
- **Real-time WebSocket streaming:** `/ws` endpoint broadcasts to multiple clients simultaneously

---

## System architecture

```
flowchart TD
    subgraph Physical Edge Layer
        A[B&K 2245 Sound Level Meter] -->|USB CDC ECM / RNDIS - usb0| B[Raspberry Pi Edge Gateway]
    end
    subgraph Linux Systemd Core
        B --> C[Python Telemetry Service]
        C --> D[Async Polling: WebXi HTTP API]
        C --> E[Thread-Safe Memory State]
    end
    subgraph Transport Layer
        B --> F[FastAPI / Uvicorn Server]
        F --> G[REST Endpoint: /]
        F --> H[WebSocket Server: /ws]
    end
    subgraph Client Layer
        H --> I[Dashboards / Monitoring Tools]
    end
```

---

## Production deployment

### 1. Environment setup

```bash
cd ~
python3 -m venv .venv
source .venv/bin/activate

git clone https://github.com/carnestoltes/bk2245-logger.git
cd bk2245-logger
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### 2. Systemd service (self-healing, auto-start)

```bash
sudo systemctl daemon-reload
sudo systemctl enable bk2245.service
sudo systemctl start bk2245.service
```

---

## Operations

```bash
# Monitor live logs
journalctl -u bk2245.service -f -n 50

# Run manually for development/debugging
uvicorn src.bk2245_logger:app --host 0.0.0.0 --port 8000 --reload

# Verify WebSocket stream from a remote machine
wscat -c ws://<RASPBERRY_PI_IP>:8000/ws
```

---

## Topics

`iot` `raspberry-pi` `edge-computing` `websocket` `fastapi` `python` `acoustic-monitoring` `industrial-iot` `data-acquisition` `systemd` `usb-networking`
