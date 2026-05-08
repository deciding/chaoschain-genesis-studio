import sqlite3
from pathlib import Path
from typing import Dict, List, Optional


class AggregationEngine:
    def __init__(self, dkg=None):
        self.dkg = dkg
        self.db_path = Path.home() / ".tradememory" / "trades.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.db_path))
        self._init_db()
        self.trade_count_since_aggregation = 0

    def _init_db(self):
        """Initialize local SQLite for trade index."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS trade_index (
                id TEXT PRIMARY KEY,
                memory_type TEXT,
                content TEXT,
                timestamp TEXT,
                uploaded_0g INTEGER DEFAULT 0
            )
        """)
        self.db.commit()

    def add_trade(self, trade: dict) -> dict:
        """Add episodic trade, auto-aggregate at 10."""
        self._store_trade(trade)
        self.trade_count_since_aggregation += 1
        if self.trade_count_since_aggregation >= 10:
            self.aggregate()
        return {"trade_id": trade["id"], "count": self.trade_count_since_aggregation}

    def aggregate(self) -> List[dict]:
        """Run SQL grouping - placeholder."""
        self.trade_count_since_aggregation = 0
        return []

    def _store_trade(self, trade: dict):
        """Store trade in local SQLite."""
        import json
        from datetime import datetime

        self.db.execute(
            """
            INSERT OR REPLACE INTO trade_index (id, memory_type, content, timestamp, uploaded_0g)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                trade["id"],
                "episodic",
                json.dumps(trade),
                datetime.utcnow().isoformat(),
                0,
            ),
        )
        self.db.commit()

    def _group_by_strategy(self) -> List[dict]:
        """SQL: Group by strategy."""
        import json

        cursor = self.db.execute(
            "SELECT id, content FROM trade_index WHERE memory_type = 'episodic'"
        )

        groups: dict = {}
        for row in cursor.fetchall():
            content = json.loads(row[1])
            strat = content.get("strategy", "unknown")
            if strat not in groups:
                groups[strat] = {
                    "strategy": strat,
                    "trades": [],
                    "wins": 0,
                    "total_pnl": 0,
                }
            groups[strat]["trades"].append(content["id"])
            pnl = content.get("pnl", 0)
            groups[strat]["total_pnl"] += pnl
            if pnl > 0:
                groups[strat]["wins"] += 1

        results = []
        for strat, data in groups.items():
            count = len(data["trades"])
            results.append(
                {
                    "strategy": strat,
                    "total_pnl": data["total_pnl"],
                    "win_rate": round(data["wins"] / count * 100, 1)
                    if count > 0
                    else 0,
                    "count": count,
                    "trade_ids": data["trades"],
                }
            )

        return results
