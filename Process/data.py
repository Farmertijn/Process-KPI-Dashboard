import pandas as pd
import json
from sqlalchemy import create_engine

# Database connection setup
DATABASE_URL = 'mariadb+mariadbconnector://root:admin@10.2.3.15:3306/1615_fieldless_historian'
engine = create_engine(DATABASE_URL)

# Function to load data from SQL using SQLAlchemy
def load_data_from_sql(query, engine):
    with engine.connect() as connection:
        return pd.read_sql(query, connection)

# Queries to get the data
query_filling_infeed = "SELECT * FROM `event` WHERE `type` = 'FILLING_INFEED'"
query_transplanting_infeed = "SELECT * FROM `event` WHERE `type` = 'TRANSPLANTING_INFEED'"
query_bench_weight = "SELECT * FROM `event` WHERE `type` = 'BENCH_WEIGHT'"

# Load data from SQL
df_filling_infeed = load_data_from_sql(query_filling_infeed, engine)
df_transplanting_infeed = load_data_from_sql(query_transplanting_infeed, engine)
df_bench_weight = load_data_from_sql(query_bench_weight, engine)

# JSON metadata
def parse_metadata(df, column):
    df_metadata = df[column].apply(json.loads).apply(pd.Series)
    df = pd.concat([df.drop(column, axis=1), df_metadata], axis=1)
    return df

df_filling_infeed = parse_metadata(df_filling_infeed, 'metadata')
df_transplanting_infeed = parse_metadata(df_transplanting_infeed, 'metadata')
df_bench_weight = parse_metadata(df_bench_weight, 'metadata')

# Ensure timestamps are in datetime format
df_filling_infeed['timestamp'] = pd.to_datetime(df_filling_infeed['timestamp'])
df_transplanting_infeed['timestamp'] = pd.to_datetime(df_transplanting_infeed['timestamp'])
df_bench_weight['crate weight timestamp'] = pd.to_datetime(df_bench_weight['crate weight timestamp'])