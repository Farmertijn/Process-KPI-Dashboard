import pandas as pd
import pytest

# Laad de transplanting infeed dataset
transplanting_infeed_data = pd.read_csv('data_exports/df_transplanting_infeed.csv', parse_dates=['timestamp'])

def test_transplanting_infeed_data_columns():
    required_columns = ["timestamp", "crop name", "bench name"]
    for col in required_columns:
        assert col in transplanting_infeed_data.columns, f"Missing column: {col}"

def test_transplanting_infeed_valid_timestamps():
    assert transplanting_infeed_data['timestamp'].notnull().all(), "Null timestamps found in transplanting infeed data"

def test_transplanting_infeed_valid_crop_names():
    assert transplanting_infeed_data['crop name'].notnull().all(), "Null crop names found in transplanting infeed data"
