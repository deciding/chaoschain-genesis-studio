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
