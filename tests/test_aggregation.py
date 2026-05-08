import pytest
from tradememory.aggregation import AggregationEngine


@pytest.fixture(autouse=True)
def clean_db():
    """Clean database before each test."""
    engine = AggregationEngine()
    engine.db.execute("DELETE FROM trade_index")
    engine.db.commit()
    yield


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


def test_auto_aggregate_at_10():
    """Test aggregation runs after 10 trades."""
    from unittest.mock import patch

    engine = AggregationEngine()

    # Add 9 trades - should NOT aggregate
    for i in range(9):
        engine.add_trade(
            {
                "id": f"trade_{i:03d}",
                "symbol": "XAUUSD",
                "direction": "long",
                "pnl": 100,
                "strategy": "breakout",
            }
        )
    assert engine.trade_count_since_aggregation == 9

    # Add 10th trade - should aggregate
    with patch.object(engine, "aggregate") as mock_agg:
        engine.add_trade(
            {
                "id": "trade_009",
                "symbol": "XAUUSD",
                "direction": "long",
                "pnl": 100,
                "strategy": "breakout",
            }
        )
        mock_agg.assert_called_once()


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


def test_group_by_symbol():
    """Test SQL grouping by symbol."""
    engine = AggregationEngine()

    engine._store_trade({"id": "t1", "symbol": "XAUUSD", "pnl": 100})
    engine._store_trade({"id": "t2", "symbol": "XAUUSD", "pnl": -50})
    engine._store_trade({"id": "t3", "symbol": "BTCUSD", "pnl": 200})

    results = engine._group_by_symbol()

    xauusd = next(r for r in results if r["symbol"] == "XAUUSD")
    assert xauusd["total_pnl"] == 50
    assert xauusd["win_rate"] == 50.0


def test_group_by_direction():
    """Test SQL grouping by direction."""
    engine = AggregationEngine()

    engine._store_trade({"id": "t1", "direction": "long", "pnl": 100})
    engine._store_trade({"id": "t2", "direction": "long", "pnl": -50})
    engine._store_trade({"id": "t3", "direction": "short", "pnl": 200})

    results = engine._group_by_direction()

    long_group = next(r for r in results if r["direction"] == "long")
    assert long_group["total_pnl"] == 50
    assert long_group["win_rate"] == 50.0


def test_group_by_strategy():
    """Test SQL grouping by strategy."""
    engine = AggregationEngine()

    trades = [
        {"id": "trade_001", "strategy": "breakout", "pnl": 100},
        {"id": "trade_002", "strategy": "breakout", "pnl": -50},
        {"id": "trade_003", "strategy": "mean_reversion", "pnl": 200},
    ]
    for t in trades:
        engine._store_trade(t)

    results = engine._group_by_strategy()

    assert len(results) == 2
    breakout = next(r for r in results if r["strategy"] == "breakout")
    assert breakout["total_pnl"] == 50
    assert breakout["win_rate"] == 50.0
    assert breakout["trade_ids"] == ["trade_001", "trade_002"]


def test_aggregate_creates_semantic():
    """Test aggregate creates semantic patterns in DKG."""
    from unittest.mock import Mock

    engine = AggregationEngine(dkg=Mock())

    engine._store_trade(
        {
            "id": "t1",
            "strategy": "breakout",
            "pnl": 100,
            "symbol": "XAUUSD",
            "direction": "long",
        }
    )
    engine._store_trade(
        {
            "id": "t2",
            "strategy": "breakout",
            "pnl": -50,
            "symbol": "XAUUSD",
            "direction": "long",
        }
    )

    patterns = engine.aggregate()

    assert len(patterns) >= 1
    engine.dkg.add_memory.assert_called()
