import pytest
from tradememory.aggregation import AggregationEngine


def test_aggregation_engine_init():
    """Test AggregationEngine initializes correctly."""
    engine = AggregationEngine()
    assert engine.trade_count_since_aggregation == 0
    assert engine.db is not None


def test_add_trade_increments_counter():
    """Test adding trade increments the counter."""
    engine = AggregationEngine()
    initial = engine.trade_count_since_aggregation
    engine.add_trade(
        {
            "id": "trade_test_001",
            "symbol": "XAUUSD",
            "direction": "long",
            "pnl": 100,
            "strategy": "breakout",
        }
    )
    assert engine.trade_count_since_aggregation == initial + 1


def test_store_trade_in_sqlite():
    """Test trade is stored in local SQLite."""
    engine = AggregationEngine()
    trade = {
        "id": "trade_xauusd_001",
        "symbol": "XAUUSD",
        "direction": "long",
        "entry": 2045,
        "pnl": 100,
        "strategy": "breakout",
    }
    engine._store_trade(trade)

    # Verify it's in SQLite
    cursor = engine.db.execute("SELECT * FROM trade_index WHERE id = ?", (trade["id"],))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == "episodic"
