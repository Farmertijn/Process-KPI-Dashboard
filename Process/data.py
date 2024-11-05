import pandas as pd
import json
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os
from datetime import datetime, timedelta

# Database connection setup
DATABASE_URL = 'mariadb+mariadbconnector://root:admin@10.2.3.15:3306/1615_fieldless_historian'
engine = create_engine(DATABASE_URL)

# Maak de map aan voor CSV-backups als deze nog niet bestaat
os.makedirs('data_exports', exist_ok=True)

# File paths voor CSV-backups in de `data_exports` map
csv_filling_infeed = 'Process/data_exports/df_filling_infeed.csv'
csv_transplanting_infeed = 'Process/data_exports/df_transplanting_infeed.csv'
csv_bench_weight = 'Process/data_exports/df_bench_weight.csv'

# Queries om de data op te halen
query_filling_infeed = "SELECT * FROM `event` WHERE `type` = 'FILLING_INFEED'"
query_transplanting_infeed = "SELECT * FROM `event` WHERE `type` = 'TRANSPLANTING_INFEED'"
query_bench_weight = "SELECT * FROM `event` WHERE `type` = 'BENCH_WEIGHT'"

# Functie om data uit SQL te laden met SQLAlchemy
def load_data_from_sql(query, engine):
    with engine.connect() as connection:
        return pd.read_sql(query, connection)

# Functie om JSON metadata te parsen
def parse_metadata(df, column):
    df_metadata = df[column].apply(json.loads).apply(pd.Series)
    df = pd.concat([df.drop(column, axis=1), df_metadata], axis=1)
    return df

# Variabele om bij te houden of data uit de database of CSV komt
using_csv_backup = False

try:
    # Probeer verbinding te maken met de database en data op te halen
    df_filling_infeed = load_data_from_sql(query_filling_infeed, engine)
    df_transplanting_infeed = load_data_from_sql(query_transplanting_infeed, engine)
    df_bench_weight = load_data_from_sql(query_bench_weight, engine)

    # Parse JSON metadata
    df_filling_infeed = parse_metadata(df_filling_infeed, 'metadata')
    df_transplanting_infeed = parse_metadata(df_transplanting_infeed, 'metadata')
    df_bench_weight = parse_metadata(df_bench_weight, 'metadata')

    # Zorg dat de timestamp-kolommen in datetime-formaat zijn
    df_filling_infeed['timestamp'] = pd.to_datetime(df_filling_infeed['timestamp'])
    df_transplanting_infeed['timestamp'] = pd.to_datetime(df_transplanting_infeed['timestamp'])
    df_bench_weight['crate weight timestamp'] = pd.to_datetime(df_bench_weight['crate weight timestamp'])

    # Exporteer de data naar CSV-bestanden in de map 'data_exports'
    df_filling_infeed.to_csv(csv_filling_infeed, index=False)
    df_transplanting_infeed.to_csv(csv_transplanting_infeed, index=False)
    df_bench_weight.to_csv(csv_bench_weight, index=False)
    print("Data succesvol geladen uit de database en geëxporteerd naar CSV-bestanden.")
    reference_date = datetime.now()

except OperationalError:
    # Als de database niet bereikbaar is, laad data uit de CSV-bestanden
    print("Database niet bereikbaar. Data wordt geladen uit CSV-bestanden.")
    using_csv_backup = True
    df_filling_infeed = pd.read_csv(csv_filling_infeed, parse_dates=['timestamp'])
    df_transplanting_infeed = pd.read_csv(csv_transplanting_infeed, parse_dates=['timestamp'])
    df_bench_weight = pd.read_csv(csv_bench_weight, parse_dates=['crate weight timestamp'])

    # Bereken de laatste datum in de CSV-bestanden
    latest_dates = [
        df_filling_infeed['timestamp'].max().replace(tzinfo=None),
        df_transplanting_infeed['timestamp'].max().replace(tzinfo=None),
        df_bench_weight['crate weight timestamp'].max().replace(tzinfo=None)
    ]
    reference_date = max(latest_dates)
    print(f"Referentiedatum voor CSV-data: {reference_date}")