#!bin/bash

ip link set eth0 up

if ! ip addr show eth0 | grep -q "192.168.0.252"; then
  ip addr add 192.168.0.252/24 dev eth0
  # ip route replace default via 192.168.0.1 dev eth0
fi

for i in $(1 30); do
  ip link show usb0 >/dev/null 2>&1 && break
  sleep 1
done

ip link set usb0 up

if ! ip addr show usb0 | grep -q "192.168.2.253"; then
  ip addr add 192.168.2.253/24 dev usb0
fi
