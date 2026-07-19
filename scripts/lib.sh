#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"

die() {
  echo "error: $*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

load_config() {
  [ -f "$ENV_FILE" ] || die "missing $ENV_FILE; copy .env.example to .env and review it"
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  PROFILE="${PROFILE:-fast}"
  PROFILE_FILE="$ROOT_DIR/profiles/$PROFILE.env"
  [ -f "$PROFILE_FILE" ] || die "unknown profile '$PROFILE' ($PROFILE_FILE not found)"
  # shellcheck disable=SC1090
  source "$PROFILE_FILE"
  if [ -n "${WORKER_SSH_OVERRIDE:-}" ]; then
    WORKER_SSH="$WORKER_SSH_OVERRIDE"
    export WORKER_SSH
  fi
  set +a
}

require_config() {
  local name
  for name in "$@"; do
    [ -n "${!name:-}" ] || die "$name must be set in $ENV_FILE"
  done
}
