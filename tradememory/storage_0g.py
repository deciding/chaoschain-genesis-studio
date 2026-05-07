"""
0G Storage adapter for TradeMemory Protocol.
Replaces SQLite with encrypted 0G Storage.
"""

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from cryptography.fernet import Fernet
import hashlib

logger = logging.getLogger(__name__)


class TradeMemory0GStorage:
    """
    TradeMemory storage backed by 0G Storage.
    """

    def __init__(self, private_key: str = None, encryption_key: bytes = None):
        self.private_key = private_key or os.getenv("ZEROG_TESTNET_PRIVATE_KEY")

        self.cache_dir = Path.home() / ".tradememory" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.encryption_key = encryption_key or self._get_or_create_key()
        self.fernet = Fernet(self.encryption_key)

        self.cid_cache_file = self.cache_dir / "cid_cache.json"
        self._load_cid_cache()

        self._storage_client = None

        print(f"TradeMemory0GStorage initialized")

    def _get_or_create_key(self) -> bytes:
        key_file = self.cache_dir / ".encryption_key"
        if key_file.exists():
            return key_file.read_bytes()
        key = Fernet.generate_key()
        key_file.write_bytes(key)
        key_file.chmod(0o600)
        return key

    def _load_cid_cache(self):
        if self.cid_cache_file.exists():
            self.cid_cache = json.loads(self.cid_cache_file.read_text())
        else:
            self.cid_cache = {}

    def _save_cid_cache(self):
        self.cid_cache_file.write_text(json.dumps(self.cid_cache, indent=2))

    def _get_storage_client(self):
        if self._storage_client is None:
            try:
                from chaoschain_sdk.storage_backends import (
                    ZeroGStorageBackend,
                    StorageConfig,
                    StorageProvider,
                )

                config = StorageConfig(provider=StorageProvider.ZEROG)
                self._storage_client = ZeroGStorageBackend(config)
                print("0G Storage client connected")
            except ImportError as e:
                print(f"Failed to import 0G storage: {e}")
                raise
        return self._storage_client

    def _encrypt(self, data: bytes) -> bytes:
        return self.fernet.encrypt(data)

    def _decrypt(self, data: bytes) -> bytes:
        return self.fernet.decrypt(data)

    def push_table(self, table_name: str, data: List[Dict]) -> str:
        if not data:
            print(f"Empty data for {table_name}, skipping upload")
            return ""

        json_data = json.dumps(
            {
                "table": table_name,
                "data": data,
                "updated_at": datetime.utcnow().isoformat(),
                "version": "1.0",
            },
            indent=2,
            default=str,
        )

        encrypted = self._encrypt(json_data.encode())

        try:
            client = self._get_storage_client()
            result = client.store(encrypted)

            if result.success:
                cid = result.uri
                self.cid_cache[table_name] = cid
                self._save_cid_cache()
                print(f"Uploaded {table_name}: {cid}")
                return cid
            else:
                raise Exception(f"Upload failed: {result.error}")
        except Exception as e:
            print(f"Failed to upload {table_name}: {e}")
            raise

    def pull_table(self, table_name: str) -> List[Dict]:
        cid = self.cid_cache.get(table_name)
        if not cid:
            print(f"No CID for {table_name}, returning empty")
            return []

        try:
            client = self._get_storage_client()
            result = client.get(cid)

            if not result.success:
                raise Exception(f"Download failed: {result.error}")

            decrypted = self._decrypt(result.data)
            parsed = json.loads(decrypted)
            return parsed.get("data", [])

        except Exception as e:
            print(f"Failed to download {table_name}: {e}")
            return []

    def remember_trade(self, trade_data: Dict) -> str:
        return self.push_table("trade_records", [trade_data])

    def recall_trades(self, filters: Dict = None) -> List[Dict]:
        trades = self.pull_table("trade_records")
        if not filters:
            return trades

        filtered = []
        for trade in trades:
            match = True
            for key, value in filters.items():
                if trade.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(trade)
        return filtered

    def remember_pattern(self, pattern_data: Dict) -> str:
        return self.push_table("patterns", [pattern_data])

    def remember_strategy_adjustment(self, adjustment: Dict) -> str:
        return self.push_table("strategy_adjustments", [adjustment])

    def update_session_state(self, state: Dict) -> str:
        return self.push_table("session_state", [state])

    def get_session_state(self, agent_id: str = "default") -> Dict:
        states = self.pull_table("session_state")
        for state in states:
            if state.get("agent_id") == agent_id:
                return state
        return {}

    def sync_all(self, db_path: str = None) -> Dict[str, str]:
        if not db_path:
            db_path = os.environ.get("TRADEMEMORY_DB", "data/tradememory.db")

        tables = [
            "trade_records",
            "session_state",
            "patterns",
            "strategy_adjustments",
            "episodic_memory",
            "semantic_memory",
            "procedural_memory",
            "affective_memory",
        ]

        results = {}

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        for table in tables:
            try:
                cursor = conn.execute(f"SELECT * FROM {table}")
                rows = [dict(row) for row in cursor.fetchall()]
                if rows:
                    cid = self.push_table(table, rows)
                    results[table] = cid
                    print(f"Synced {table}: {len(rows)} records")
            except Exception as e:
                print(f"Failed to sync {table}: {e}")

        conn.close()
        return results


def create_0g_storage(private_key: str = None) -> TradeMemory0GStorage:
    return TradeMemory0GStorage(private_key=private_key)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        storage = TradeMemory0GStorage()
        results = storage.sync_all()
        print("Sync results:")
        for table, cid in results.items():
            print(f"  {table}: {cid}")
    else:
        print("TradeMemory0GStorage loaded")
        print("Usage: python storage_0g.py sync  # Sync SQLite to 0G")
