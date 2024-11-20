import pandas as pd
import pytest

# Laad de bench weight dataset
bench_weight_data = pd.read_csv('data_exports/df_bench_weight.csv', parse_dates=['crate weight timestamp'])

def test_bench_weight_data_columns():
    required_columns = ["crate weight timestamp", "crop name", "weight in kilograms"]
    for col in required_columns:
        assert col in bench_weight_data.columns, f"Missing column: {col}"

def test_bench_weight_valid_timestamps():
    assert bench_weight_data['crate weight timestamp'].notnull().all(), "Null timestamps found in bench weight data"

def test_bench_weight_positive_weights():
    bench_weight_data_filtered = bench_weight_data[bench_weight_data['weight in kilograms'] > 0]
    assert not bench_weight_data_filtered.empty, "No valid weights found after filtering"

def test_bench_weight_valid_crop_names():
    assert bench_weight_data['crop name'].notnull().all(), "Null crop names found in bench weight data"
