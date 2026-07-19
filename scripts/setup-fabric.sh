#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: sudo $0 <head|worker> <active-interface>" >&2
  echo "example Forge: sudo $0 head enp1s0f0np0" >&2
  echo "example Anvil: sudo $0 worker enp1s0f1np1" >&2
  exit 2
}

[ "$#" -eq 2 ] || usage
[ "$(id -u)" -eq 0 ] || { echo "run this script with sudo" >&2; exit 1; }

role="$1"
interface="$2"
case "$role" in
  head) address="10.100.10.1/24"; peer="10.100.10.2" ;;
  worker) address="10.100.10.2/24"; peer="10.100.10.1" ;;
  *) usage ;;
esac

ip link show "$interface" >/dev/null 2>&1 || {
  echo "interface does not exist: $interface" >&2
  ibdev2netdev || true
  exit 1
}

state="$(cat "/sys/class/net/$interface/operstate")"
[ "$state" = "up" ] || {
  echo "$interface is not up (state=$state); verify the QSFP cable/port" >&2
  exit 1
}

config=/etc/netplan/40-dual-spark.yaml
if [ -e "$config" ]; then
  cp -a "$config" "$config.backup.$(date +%Y%m%d-%H%M%S)"
fi

cat >"$config" <<EOF
network:
  version: 2
  ethernets:
    $interface:
      addresses:
        - $address
      dhcp4: false
      dhcp6: false
      optional: true
EOF

chmod 600 "$config"
netplan generate
netplan apply

echo "Configured $role $interface as $address"
ip -4 addr show dev "$interface"
echo "RoCE GIDs after configuration:"
show_gids 2>/dev/null | awk -v dev="$interface" 'NR <= 2 || $NF == dev'
echo "Peer test (it is normal for this to fail until both nodes are configured):"
ping -c 2 -W 1 "$peer" || true
