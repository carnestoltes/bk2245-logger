#!/bin/bash
set -e

echo "=== Ensuring NetworkManager ignores eth0 and usb0 ==="
NM_CONF_DIR="/host/etc/NetworkManager/conf.d"

if [ -d "$NM_CONF_DIR" ]; then
  if [ ! -f "$NM_CONF_DIR/99-unmanaged-devices.conf" ]; then
    echo "Creating NetworkManager override file..."
    cat <<EOF > "$NM_CONF_DIR/99-unmanaged-devices.conf"
[main]
plugins=ifcfg-rh,keyfile

[keyfile]
unmanaged-devices=interface-name:eth0;interface-name:usb0
EOF
    echo "Reloading NetworkManager..."
    nmcli connection reload || true
  else
    echo "NetworkManager override file already exists."
  fi
else
  echo "WARNING: Host /etc/NetworkManager/conf.d not found. Skipping config."
fi

echo "=== Configuring Network Interfaces ==="

ip link set eth0 up
if ! ip addr show eth0 | grep -q "192.168.0.252"; then
  echo "Assigning 192.168.0.252 to eth0..."
  ip addr add 192.168.0.252/24 dev eth0
fi

echo "Waiting for usb0 interface..."
for i in $(seq 1 30); do
  ip link show usb0 >/dev/null 2>&1 && break
  sleep 1
done

if ip link show usb0 >/dev/null 2>&1; then
  ip link set usb0 up
  if ! ip addr show usb0 | grep -q "192.168.2.253"; then
    echo "Assigning 192.168.2.253 to usb0..."
    ip addr add 192.168.2.253/24 dev usb0
  fi
else
  echo "WARNING: usb0 interface not found after 30 seconds."
fi

echo "=== Network Configuration Complete ==="
exec "$@"
