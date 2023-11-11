import pytest
from decimal import Decimal
from sma_strategy import df


@pytest.fixture
def sample_dataframe():
    return df


def test_input_types(sample_dataframe):
    # Check if input types are as expected
    assert sample_dataframe["datetime"].dtype == "datetime64[ns]"
    assert all(isinstance(value, Decimal) for value in sample_dataframe["close"])
    assert all(isinstance(value, Decimal) for value in sample_dataframe["high"])
    assert all(isinstance(value, Decimal) for value in sample_dataframe["low"])
    assert all(isinstance(value, Decimal) for value in sample_dataframe["open"])
    assert sample_dataframe["volume"].dtype == "int64"
    assert all(isinstance(value, str) for value in sample_dataframe["instrument"])
