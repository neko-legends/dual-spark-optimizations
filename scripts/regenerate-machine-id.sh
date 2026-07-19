#!/usr/bin/env bash
set -euo pipefail

expected_hostname="${1:?usage: sudo $0 EXPECTED_HOSTNAME}"
[ "$(id -u)" -eq 0 ] || { echo "run this script with sudo" >&2; exit 1; }
[ "$(hostname)" = "$expected_hostname" ] || {
  echo "refusing: expected hostname '$expected_hostname', found '$(hostname)'" >&2
  exit 1
}

old_id="$(cat /etc/machine-id)"
backup_dir="/root/machine-id-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -m 700 "$backup_dir"
cp -a /etc/machine-id "$backup_dir/machine-id"
if [ -e /var/lib/dbus/machine-id ] || [ -L /var/lib/dbus/machine-id ]; then
  cp -a /var/lib/dbus/machine-id "$backup_dir/dbus-machine-id"
fi

: >/etc/machine-id
systemd-machine-id-setup --root=/ >/dev/null
new_id="$(cat /etc/machine-id)"

if [ -z "$new_id" ] || [ "$new_id" = "$old_id" ]; then
  cp -a "$backup_dir/machine-id" /etc/machine-id
  echo "failed to generate a distinct machine ID; restored the original" >&2
  exit 1
fi

echo "Machine ID changed on $(hostname)."
echo "old=$old_id"
echo "new=$new_id"
echo "backup=$backup_dir"
echo "Reboot this node now, then verify the two nodes have different machine IDs."
