#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
VENV_PY="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

if ! "$VENV_PY" -c "import chaoschain_sdk, flask, dotenv, rich" >/dev/null 2>&1; then
  "$VENV_PY" -m pip install --upgrade pip
  "$VENV_PIP" install chaoschain-sdk flask python-dotenv rich
fi

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if [ "${NETWORK:-}" != "0g-testnet" ]; then
  echo "[WARN] NETWORK is '${NETWORK:-<unset>}' (expected '0g-testnet')."
fi

if [ "${ZEROG_TESTNET_RPC_URL:-}" = "" ]; then
  echo "[WARN] ZEROG_TESTNET_RPC_URL is missing in .env"
fi

LLM_PROVIDER="${LLM_PROVIDER:-crewai}"
if [ "$LLM_PROVIDER" = "0g" ] && [ "${ZEROG_TESTNET_PRIVATE_KEY:-}" = "" ]; then
  echo "[STOP] LLM_PROVIDER=0g requires ZEROG_TESTNET_PRIVATE_KEY in .env"
  exit 1
fi
if [ "$LLM_PROVIDER" = "crewai" ] && [ "${OPENAI_API_KEY:-}" = "" ]; then
  echo "[STOP] LLM_PROVIDER=crewai requires OPENAI_API_KEY in .env"
  exit 1
fi

WALLET_FILE="$ROOT_DIR/chaoschain_wallets.json"
if [ "$LLM_PROVIDER" = "0g" ] && [ "${ZEROG_TESTNET_PRIVATE_KEY:-}" != "" ] && [ "${ZEROG_TESTNET_PRIVATE_KEY}" != "0xPASTE"* ]; then
  ROOT_DIR="$ROOT_DIR" WALLET_FILE="$WALLET_FILE" ZEROG_TESTNET_PRIVATE_KEY="$ZEROG_TESTNET_PRIVATE_KEY" "$VENV_PY" - <<'PY'
import json, os
from pathlib import Path
from eth_account import Account

wallet_file = Path(os.environ["WALLET_FILE"])
pk = os.environ["ZEROG_TESTNET_PRIVATE_KEY"].strip()
acct = Account.from_key(pk)

if wallet_file.exists():
    data = json.loads(wallet_file.read_text())
else:
    data = {}

for n in ("Alice","Bob","Charlie"):
    data[n] = {"address": acct.address, "private_key": pk}

wallet_file.write_text(json.dumps(data, indent=2) + "\n")
print(f"[WALLET] Using ZEROG_TESTNET_PRIVATE_KEY for all agents: {acct.address}")
PY
fi

echo "Running Genesis Studio on 0G testnet (LLM_PROVIDER=$LLM_PROVIDER)..."
exec "$VENV_PY" "$ROOT_DIR/genesis_studio.py"
