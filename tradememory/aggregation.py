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
        """Run SQL grouping → create semantic patterns in DKG."""
        patterns = []

        if self.dkg is None:
            self.trade_count_since_aggregation = 0
            return patterns

        for sp in self._group_by_strategy():
            if sp["count"] >= 2:
                semantic = self.dkg.add_memory(
                    f"semantic_strategy_{sp['strategy']}",
                    "semantic",
                    {
                        "pattern_type": "strategy",
                        "strategy": sp["strategy"],
                        "total_pnl": sp["total_pnl"],
                        "win_rate": sp["win_rate"],
                        "count": sp["count"],
                    },
                    caused_by=sp["trade_ids"],
                )
                patterns.append(semantic)

        for sp in self._group_by_symbol():
            if sp["count"] >= 2:
                semantic = self.dkg.add_memory(
                    f"semantic_symbol_{sp['symbol']}",
                    "semantic",
                    {
                        "pattern_type": "symbol",
                        "symbol": sp["symbol"],
                        "total_pnl": sp["total_pnl"],
                        "win_rate": sp["win_rate"],
                        "count": sp["count"],
                    },
                    caused_by=sp["trade_ids"],
                )
                patterns.append(semantic)

        for sp in self._group_by_direction():
            if sp["count"] >= 2:
                semantic = self.dkg.add_memory(
                    f"semantic_direction_{sp['direction']}",
                    "semantic",
                    {
                        "pattern_type": "direction",
                        "direction": sp["direction"],
                        "total_pnl": sp["total_pnl"],
                        "win_rate": sp["win_rate"],
                        "count": sp["count"],
                    },
                    caused_by=sp["trade_ids"],
                )
                patterns.append(semantic)

        self.trade_count_since_aggregation = 0
        return patterns

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

    def _group_by_symbol(self) -> List[dict]:
        """SQL: Group by symbol."""
        import json

        cursor = self.db.execute(
            "SELECT id, content FROM trade_index WHERE memory_type = 'episodic'"
        )

        groups: dict = {}
        for row in cursor.fetchall():
            content = json.loads(row[1])
            sym = content.get("symbol", "unknown")
            if sym not in groups:
                groups[sym] = {
                    "symbol": sym,
                    "trades": [],
                    "wins": 0,
                    "total_pnl": 0,
                }
            groups[sym]["trades"].append(content["id"])
            pnl = content.get("pnl", 0)
            groups[sym]["total_pnl"] += pnl
            if pnl > 0:
                groups[sym]["wins"] += 1

        results = []
        for sym, data in groups.items():
            count = len(data["trades"])
            results.append(
                {
                    "symbol": sym,
                    "total_pnl": data["total_pnl"],
                    "win_rate": round(data["wins"] / count * 100, 1)
                    if count > 0
                    else 0,
                    "count": count,
                    "trade_ids": data["trades"],
                }
            )

        return results

    def _group_by_direction(self) -> List[dict]:
        """SQL: Group by direction."""
        import json

        cursor = self.db.execute(
            "SELECT id, content FROM trade_index WHERE memory_type = 'episodic'"
        )

        groups: dict = {}
        for row in cursor.fetchall():
            content = json.loads(row[1])
            direction = content.get("direction", "unknown")
            if direction not in groups:
                groups[direction] = {
                    "direction": direction,
                    "trades": [],
                    "wins": 0,
                    "total_pnl": 0,
                }
            groups[direction]["trades"].append(content["id"])
            pnl = content.get("pnl", 0)
            groups[direction]["total_pnl"] += pnl
            if pnl > 0:
                groups[direction]["wins"] += 1

        results = []
        for direction, data in groups.items():
            count = len(data["trades"])
            results.append(
                {
                    "direction": direction,
                    "total_pnl": data["total_pnl"],
                    "win_rate": round(data["wins"] / count * 100, 1)
                    if count > 0
                    else 0,
                    "count": count,
                    "trade_ids": data["trades"],
                }
            )

        return results
