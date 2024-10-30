import pandas as pd
from datetime import datetime, timedelta
import pytz
from data import df_filling_infeed, df_transplanting_infeed, df_bench_weight, reference_date, using_csv_backup

et = pytz.timezone('America/Toronto')


def localize_and_convert(df, column, target_timezone):
    if df[column].dt.tz is None:
        df[column] = df[column].dt.tz_localize('UTC').dt.tz_convert(target_timezone)
    else:
        df[column] = df[column].dt.tz_convert(target_timezone)
    return df


df_filling_infeed = localize_and_convert(df_filling_infeed, 'timestamp', et)
df_transplanting_infeed = localize_and_convert(df_transplanting_infeed, 'timestamp', et)
df_bench_weight = localize_and_convert(df_bench_weight, 'crate weight timestamp', et)

current_date = reference_date if using_csv_backup else datetime.now(et)
today = current_date.date()
yesterday = today - timedelta(days=1)
last_week = today - timedelta(days=7)
day_before_yesterday = yesterday - timedelta(days=1)
two_weeks_ago = last_week - timedelta(days=7)

def filter_and_calculate(df_filling_infeed, df_transplanting_infeed, df_bench_weight, date=None, start_date=None,
                         end_date=None):
    if date:
        data_filling_infeed = df_filling_infeed[df_filling_infeed['timestamp'].dt.date == date]
        data_transplanting_infeed = df_transplanting_infeed[df_transplanting_infeed['timestamp'].dt.date == date]
        data_bench_weight = df_bench_weight[df_bench_weight['crate weight timestamp'].dt.date == date]
    elif start_date and end_date:
        data_filling_infeed = df_filling_infeed[(df_filling_infeed['timestamp'].dt.date >= start_date) & (
                    df_filling_infeed['timestamp'].dt.date < end_date)]
        data_transplanting_infeed = df_transplanting_infeed[
            (df_transplanting_infeed['timestamp'].dt.date >= start_date) & (
                        df_transplanting_infeed['timestamp'].dt.date < end_date)]
        data_bench_weight = df_bench_weight[(df_bench_weight['crate weight timestamp'].dt.date >= start_date) & (
                    df_bench_weight['crate weight timestamp'].dt.date < end_date)]

    data_bench_weight = data_bench_weight[data_bench_weight['crop name'] != 'Crop not found']

    unique_transplant_jobs = data_transplanting_infeed.drop_duplicates(subset=['transplant job bench name'])

    total_harvest = data_bench_weight['weight in kilograms'].sum()
    total_timestamps_filling_infeed = data_filling_infeed.shape[0]
    total_timestamps_transplanting_infeed = data_transplanting_infeed.shape[0]
    total_timestamps_bench_weight = data_bench_weight.shape[0]

    average_yield = total_harvest / total_timestamps_bench_weight if total_timestamps_bench_weight else 0
    total_infeed = total_timestamps_filling_infeed + total_timestamps_transplanting_infeed
    total_outfeed = total_timestamps_bench_weight + unique_transplant_jobs.shape[0]

    outfeed_events = combine_outfeed_events(data_bench_weight, unique_transplant_jobs)

    return {
        'total_harvest': total_harvest,
        'total_infeed': total_infeed,
        'total_outfeed': total_outfeed,
        'total_timestamps_bench_weight': total_timestamps_bench_weight,
        'average_yield': average_yield,
        'total_timestamps_filling_infeed': total_timestamps_filling_infeed,
        'total_timestamps_transplanting_infeed': total_timestamps_transplanting_infeed,
        'transplanting_infeed_15MIN': calculate_15MIN_frequency(data_transplanting_infeed, date, start_date,
                                                                'timestamp'),
        'outfeed_15MIN': calculate_15MIN_frequency(outfeed_events, date, start_date, 'timestamp'),
        'data_filling_infeed': data_filling_infeed,
        'data_bench_weight': data_bench_weight,
        'data_bench_weight_15MIN': calculate_15MIN_frequency(data_bench_weight, date, start_date,
                                                             'crate weight timestamp'),
        'unique_transplant_jobs_15MIN': calculate_15MIN_frequency(unique_transplant_jobs, date, start_date, 'timestamp')
    }


def combine_outfeed_events(df_bench_weight, df_unique_transplant_jobs):
    df_bench_weight = df_bench_weight[['crate weight timestamp']].rename(
        columns={'crate weight timestamp': 'timestamp'})
    df_unique_transplant_jobs = df_unique_transplant_jobs[['timestamp']].rename(columns={'timestamp': 'timestamp'})

    combined_df = pd.concat([df_bench_weight, df_unique_transplant_jobs])
    return combined_df


def calculate_15MIN_frequency(df, date=None, start_date=None, timestamp_column='timestamp'):
    df = df.copy()
    if date:
        df['time_group'] = df[timestamp_column].dt.floor('15min')  # Gebruik '15min' in plaats van '15T'
    elif start_date:
        df['time_group'] = df[timestamp_column].dt.date
    half_hourly_counts = df.groupby('time_group').size().reset_index(name='counts')
    return half_hourly_counts


def calculate_change(new_value, old_value):
    if isinstance(new_value, (int, float)) and isinstance(old_value, (int, float)):
        if old_value == 0:
            return None
        change = new_value - old_value
        return change
    return None


def get_changes(new_metrics, old_metrics):
    changes = {}
    for key in new_metrics:
        if key in old_metrics:
            changes[key] = calculate_change(new_metrics[key], old_metrics[key])
    return changes


metrics = {
    'today': filter_and_calculate(df_filling_infeed, df_transplanting_infeed, df_bench_weight, date=today),
    'yesterday': filter_and_calculate(df_filling_infeed, df_transplanting_infeed, df_bench_weight, date=yesterday),
    'week': filter_and_calculate(df_filling_infeed, df_transplanting_infeed, df_bench_weight, start_date=last_week,
                                 end_date=today),
    'day_before_yesterday': filter_and_calculate(df_filling_infeed, df_transplanting_infeed, df_bench_weight,
                                                 date=day_before_yesterday),
    'two_weeks_ago': filter_and_calculate(df_filling_infeed, df_transplanting_infeed, df_bench_weight,
                                          start_date=two_weeks_ago, end_date=last_week),
}

metrics['changes_yesterday'] = get_changes(metrics['yesterday'], metrics['day_before_yesterday'])
metrics['changes_week'] = get_changes(metrics['week'], metrics['two_weeks_ago'])