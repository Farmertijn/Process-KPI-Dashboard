import pandas as pd
import json
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os
from datetime import datetime

# Database verbinding configureren
DATABASE_URL = 'mariadb+mariadbconnector://root:admin@10.2.3.15:3306/1615_fieldless_historian'
engine = create_engine(DATABASE_URL)

# Map aanmaken voor CSV-backups (indien niet aanwezig)
os.makedirs('data_exports', exist_ok=True)

# Paden naar CSV-backups
csv_filling_infeed = 'data_exports/df_filling_infeed.csv'
csv_transplanting_infeed = 'data_exports/df_transplanting_infeed.csv'
csv_bench_weight = 'data_exports/df_bench_weight.csv'

# SQL-queries voor het ophalen van data
query_filling_infeed = "SELECT * FROM `event` WHERE `type` = 'FILLING_INFEED'"
query_transplanting_infeed = "SELECT * FROM `event` WHERE `type` = 'TRANSPLANTING_INFEED'"
query_bench_weight = "SELECT * FROM `event` WHERE `type` = 'BENCH_WEIGHT'"

# Functie om data uit SQL-database te laden
def load_data_from_sql(query, engine):
    with engine.connect() as connection:
        return pd.read_sql(query, connection)

# Functie om JSON-metadata uit een kolom te parsen
def parse_metadata(df, column):
    df_metadata = df[column].apply(json.loads).apply(pd.Series)  # Parse JSON naar kolommen
    df = pd.concat([df.drop(column, axis=1), df_metadata], axis=1)  # Voeg nieuwe kolommen toe aan DataFrame
    return df

# Variabele om aan te geven of CSV-backups worden gebruikt
using_csv_backup = False

try:
    # Probeer data op te halen uit de database
    df_filling_infeed = load_data_from_sql(query_filling_infeed, engine)
    df_transplanting_infeed = load_data_from_sql(query_transplanting_infeed, engine)
    df_bench_weight = load_data_from_sql(query_bench_weight, engine)

    # Parse metadata kolommen
    df_filling_infeed = parse_metadata(df_filling_infeed, 'metadata')
    df_transplanting_infeed = parse_metadata(df_transplanting_infeed, 'metadata')
    df_bench_weight = parse_metadata(df_bench_weight, 'metadata')

    # Converteer tijdstempels naar datetime-objecten
    df_filling_infeed['timestamp'] = pd.to_datetime(df_filling_infeed['timestamp'])
    df_transplanting_infeed['timestamp'] = pd.to_datetime(df_transplanting_infeed['timestamp'])
    df_bench_weight['crate weight timestamp'] = pd.to_datetime(df_bench_weight['crate weight timestamp'])

    # Sla de opgehaalde data op als CSV-backup
    df_filling_infeed.to_csv(csv_filling_infeed, index=False)
    df_transplanting_infeed.to_csv(csv_transplanting_infeed, index=False)
    df_bench_weight.to_csv(csv_bench_weight, index=False)
    print("Data succesvol geladen uit de database en geëxporteerd naar CSV-bestanden.")

    # Referentiedatum voor verdere verwerking
    reference_date = datetime.now()

except OperationalError:
    # Fallback: Data laden uit CSV-bestanden als database niet bereikbaar is
    print("Database niet bereikbaar. Data wordt geladen uit CSV-bestanden.")
    using_csv_backup = True

    # Laad CSV-bestanden
    df_filling_infeed = pd.read_csv(csv_filling_infeed, parse_dates=['timestamp'])
    df_transplanting_infeed = pd.read_csv(csv_transplanting_infeed, parse_dates=['timestamp'])
    df_bench_weight = pd.read_csv(csv_bench_weight, parse_dates=['crate weight timestamp'])

    # Bepaal de laatste datum van de data in de CSV-bestanden
    latest_dates = [
        df_filling_infeed['timestamp'].max().replace(tzinfo=None),
        df_transplanting_infeed['timestamp'].max().replace(tzinfo=None),
        df_bench_weight['crate weight timestamp'].max().replace(tzinfo=None)
    ]
    reference_date = max(latest_dates)  # Gebruik de meest recente datum als referentie
    print(f"Referentiedatum voor CSV-data: {reference_date}")