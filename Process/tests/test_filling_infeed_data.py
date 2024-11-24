import pandas as pd
import pytest

# Laad de filling infeed dataset
filling_infeed_data = pd.read_csv('data_exports/df_filling_infeed.csv', parse_dates=['timestamp'])

def test_filling_infeed_data_columns():
    required_columns = ["timestamp", "crop name", "bench name"]
    for col in required_columns:
        assert col in filling_infeed_data.columns, f"Missing column: {col}"

def test_filling_infeed_valid_timestamps():
    assert filling_infeed_data['timestamp'].notnull().all(), "Null timestamps found in filling infeed data"

def test_filling_infeed_valid_crop_names():
    assert filling_infeed_data['crop name'].notnull().all(), "Null crop names found in filling infeed data"
