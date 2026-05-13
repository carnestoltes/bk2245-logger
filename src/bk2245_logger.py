#!/usr/bin/env python3

import subprocess
import ipaddress
import requests
import csv
import re
from datetime import datetime
from pathlib import Path

LOGFILE = "/home/pi/bk2245-logger/data/bk2245.csv"
API_PATH = "/api/measurement"
TIMEOUT = 0.5


def get_usb_subnet():
    try:
        out = subprocess.check_output(["ip", "a", "show", "usb0"]).decode()
    except:
        out = subprocess.check_output(["ip", "a"]).decode()

    m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", out)
    if not m:
        return None

    ip = m.group(1)
    net = ".".join(ip.split(".")[:3]) + ".0/24"
    return ipaddress.ip_network(net, strict=False)


def find_bk_ip():
    subnet = get_usb_subnet()
    if not subnet:
        return None

    for host in subnet.hosts():
        url = f"http://{host}{API_PATH}"
        try:
            r = requests.get(url, timeout=TIMEOUT)
            if r.status_code == 200 and "LAeq" in r.text:
                return str(host)
        except:
            pass

    return None


def get_measurement(ip):
    url = f"http://{ip}{API_PATH}"
    r = requests.get(url, timeout=2)
    r.raise_for_status()
    return r.json()


def save(data):
    file_exists = Path(LOGFILE).exists()

    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "laeq": data.get("LAeq"),
        "lmax": data.get("Lmax"),
        "lpeak": data.get("LPeak"),
    }

    with open(LOGFILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def main():
    ip = find_bk_ip()

    if not ip:
        print("B&K not found")
        return

    data = get_measurement(ip)
    save(data)

    print(f"Logged data from {ip}")


if __name__ == "__main__":
    main()