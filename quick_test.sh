#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"
WALLET_FILE="$ROOT_DIR/chaoschain_wallets.json"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

if ! "$VENV_PY" -c "import chaoschain_sdk, flask" >/dev/null 2>&1; then
  "$VENV_PY" -m pip install --upgrade pip
  "$VENV_PIP" install chaoschain-sdk flask
fi

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if [ "${BASE_SEPOLIA_PRIVATE_KEY:-}" != "" ] && [ "${BASE_SEPOLIA_PRIVATE_KEY}" != "0xPASTE_YOUR_TEST_WALLET_PRIVATE_KEY_HERE" ]; then
  ROOT_DIR="$ROOT_DIR" WALLET_FILE="$WALLET_FILE" BASE_SEPOLIA_PRIVATE_KEY="$BASE_SEPOLIA_PRIVATE_KEY" "$VENV_PY" - <<'PY'
import json
import os
from pathlib import Path
from eth_account import Account

root = Path(os.environ["ROOT_DIR"])
wallet_file = Path(os.environ["WALLET_FILE"])
private_key = os.environ["BASE_SEPOLIA_PRIVATE_KEY"].strip()
account = Account.from_key(private_key)

if wallet_file.exists():
    data = json.loads(wallet_file.read_text())
else:
    data = {}

for agent_name in ("DemoAgent", "IntegrityDemo", "PaymentDemo"):
    data[agent_name] = {
        "address": account.address,
        "private_key": private_key,
    }

wallet_file.write_text(json.dumps(data, indent=2) + "\n")
print(f"Using BASE_SEPOLIA_PRIVATE_KEY wallet for demo agents: {account.address}")
PY
fi

exec "$VENV_PY" "$ROOT_DIR/demo_base_install.py"
