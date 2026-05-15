# B&K 2245 Raspberry Pi Logger

This project collects sound level measurements from a Brüel & Kjær 2245 sound level meter via HTTP API and stores them locally in CSV format using a Raspberry Pi.

---

## Features

- Auto-detects B&K device over USB Ethernet
- Reads measurement via HTTP API
- Logs data every 10 minutes
- Stores results in CSV format
- Runs automatically via systemd timer

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
sudo cp systemd/bk2245.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now bk2245.timer
```
## Debug

```bash
journalctl -u bk2245.service -f
systemctl list-timers
```
## Considerations

```bash
arp -a IP_sonometer_network
nmap -Pn IP_sonometer_network
nmap -sV IP_sonometer_network
```

```bash
ip addr add IP_range_sonometer dev usbx
ip link set usbx up
```
