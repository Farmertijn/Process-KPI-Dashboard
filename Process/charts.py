import seaborn as sns
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from matplotlib.ticker import MaxNLocator
import pandas as pd
import pytz
import re

plt.switch_backend('Agg')

def extract_text_in_parentheses(text):
    match = re.search(r'\((.*?)\)', text)
    return match.group(1) if match else text

def generate_transplanting_infeed_chart(data, period):
    if not data.empty:
        fig, ax = plt.subplots()
        
        ax.fill_between(
            data['time_group'],
            data['counts'],
            step='mid',
            color='#00637A'
        )
        
        
        ax.step(data['time_group'], data['counts'], where='mid', color='#00637A', linewidth=2.5)
        
        ax.set_title('Transplanted Benches versus Time')
        ax.set_xlabel('Time' if period != 'week' else 'Date')
        ax.set_ylabel('Benches')
        
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        if period == 'week':
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))    
        if period in ['today', 'yesterday']:
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H', tz=pytz.timezone('America/Toronto')))   
        
        
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        ax.set_ylim(bottom=0)
        ax.set_xlim(data['time_group'].min(), data['time_group'].max())
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        return encoded_image
    return ""

def generate_filling_infeed_chart(data: pd.DataFrame) -> str:
    if not data.empty:
        fig, ax = plt.subplots()
        crop_counts = data['crop name'].value_counts().reset_index()
        crop_counts.columns = ['crop name', 'counts']
        crop_counts['short name'] = crop_counts['crop name'].apply(extract_text_in_parentheses)
        
        barplot = sns.barplot(data=crop_counts, x='short name', y='counts', ax=ax)
        bar_color = '#00637A'
        for bar in barplot.patches:
            bar.set_facecolor(bar_color)
        
        ax.set_title('Filling Infeed by Crop Name')
        ax.set_xlabel('')
        ax.set_ylabel('Benches')

        
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        for p in barplot.patches:
            height = p.get_height()
            barplot.text(
                p.get_x() + p.get_width() / 2., 
                height / 2, 
                int(height), 
                ha="center", 
                va="center", 
                color="white", 
                fontsize=12, 
                weight="bold"
            )

        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_bar_image = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        return encoded_bar_image
    return ""

def generate_outfeed_chart(outfeed_data: pd.DataFrame, period: str, bench_weight_data, unique_transplant_jobs_data):
    if not outfeed_data.empty:
        fig, ax = plt.subplots()
        
        combined_data = pd.DataFrame({
            'time_group': outfeed_data['time_group'],
            'bench_weight_counts': bench_weight_data['counts'] if not bench_weight_data.empty else 0,
            'unique_transplant_jobs_counts': unique_transplant_jobs_data['counts'] if not unique_transplant_jobs_data.empty else 0
        }).fillna(0)
        
        combined_data['cumulative_bench_weight'] = combined_data['bench_weight_counts'].cumsum()
        combined_data['cumulative_unique_transplant_jobs'] = combined_data['unique_transplant_jobs_counts'].cumsum()
        
        ax.fill_between(combined_data['time_group'], 0, combined_data['cumulative_bench_weight'], color='#00637A', alpha=1.0, label='To Harvester')
        ax.fill_between(combined_data['time_group'], combined_data['cumulative_bench_weight'], combined_data['cumulative_bench_weight'] + combined_data['cumulative_unique_transplant_jobs'], color='#137C91', alpha=1.0, label='To Transplanting')
        
        ax.set_title('Outfeed Events versus Time')
        ax.set_xlabel('Time' if period != 'week' else 'Date')
        ax.set_ylabel('Benches')
        
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        if period == 'week':
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
        
        if period in ['today', 'yesterday']:
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H', tz=pytz.timezone('America/Toronto'))) 
        
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(loc='upper left')
        
        ax.set_ylim(bottom=0)
        ax.set_xlim(outfeed_data['time_group'].min(), outfeed_data['time_group'].max())
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_outfeed_image = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        return encoded_outfeed_image
    return ""

def generate_harvested_benches_chart(data):
    if not data.empty:
        fig, ax = plt.subplots()
        crop_counts = data['crop name'].value_counts().reset_index()
        crop_counts.columns = ['crop name', 'counts']
        crop_counts['short name'] = crop_counts['crop name'].apply(extract_text_in_parentheses)
        
        barplot = sns.barplot(data=crop_counts, x='short name', y='counts', ax=ax)
        bar_color = '#00637A'
        for bar in barplot.patches:
            bar.set_facecolor(bar_color)
        
        ax.set_title('Harvested benches by Crop Name')
        ax.set_xlabel('')
        ax.set_ylabel('Benches')
        
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        for p in barplot.patches:
            height = p.get_height()
            barplot.text(
                p.get_x() + p.get_width() / 2., 
                height / 2, 
                int(height), 
                ha="center", 
                va="center", 
                color="white", 
                fontsize=12, 
                weight="bold"
            )

        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_harvested_benches_image = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        return encoded_harvested_benches_image
    return ""

def generate_harvested_weight_chart(data):
    if not data.empty:
        fig, ax = plt.subplots()
        crop_weights = data.groupby('crop name')['weight in kilograms'].sum().reset_index()
        crop_weights.columns = ['crop name', 'total_weight']
        crop_weights['short name'] = crop_weights['crop name'].apply(extract_text_in_parentheses)

        barplot = sns.barplot(data=crop_weights, x='short name', y='total_weight', ax=ax)
        bar_color = '#00637A'
        for bar in barplot.patches:
            bar.set_facecolor(bar_color)
        
        ax.set_title('Harvested kilograms by Crop Name')
        ax.set_xlabel('')
        ax.set_ylabel('Total Kilograms')

        for p in barplot.patches:
            height = p.get_height()
            barplot.text(
                p.get_x() + p.get_width() / 2., 
                height / 2, 
                f'{height:.1f}', 
                ha="center", 
                va="center", 
                color="white", 
                fontsize=12, 
                weight="bold"
            )

        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.getvalue()).decode()

        plt.close(fig)
        return encoded_image
    return ""

def generate_average_yield_chart(data):
    if not data.empty:
        fig, ax = plt.subplots()
        
        crop_weights = data.groupby('crop name').agg(
            total_weight=('weight in kilograms', 'sum'),
            total_benches=('crate weight timestamp', 'count')
        ).reset_index()
        
        crop_weights['average_yield'] = crop_weights['total_weight'] / crop_weights['total_benches']
        crop_weights['short name'] = crop_weights['crop name'].apply(extract_text_in_parentheses)
        
        barplot = sns.barplot(data=crop_weights, x='short name', y='average_yield', ax=ax)
        bar_color = '#00637A'
        for bar in barplot.patches:
            bar.set_facecolor(bar_color)
        
        ax.set_title('Average Yield by Crop Name')
        ax.set_xlabel('')
        ax.set_ylabel('Average KG/Bench')
        
        for p in barplot.patches:
            height = p.get_height()
            barplot.text(
                p.get_x() + p.get_width() / 2., 
                height / 2, 
                f'{height:.2f}', 
                ha="center", 
                va="center", 
                color="white", 
                fontsize=12, 
                weight="bold"
            )

        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.getvalue()).decode()

        plt.close(fig)
        return encoded_image
    return ""

def generate_total_harvest_chart(data, period):
    if not data.empty and period == 'week':
        data['time_group'] = data['crate weight timestamp'].dt.floor('D')
        grouped_data = data.groupby('time_group').agg(total_harvest=('weight in kilograms', 'sum')).reset_index()
        
        fig, ax = plt.subplots()
        grouped_data = grouped_data.sort_values('time_group')
        
        ax.bar(
            grouped_data['time_group'],
            grouped_data['total_harvest'],
            width=1.0,
            color='#00637A',
            edgecolor='white',
            linewidth=0.5,
            align='center'
        )
        
        for x, y in zip(grouped_data['time_group'], grouped_data['total_harvest']):
            ax.text(x, y / 2, f'{y:.1f}', ha='center', va='center', color='white', fontsize=10, weight='bold')
        
        ax.set_title('Total Harvest versus Time')
        ax.set_xlabel('')
        ax.set_ylabel('Total Harvest (KG)')
        
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
        for label in ax.get_xticklabels():
            label.set_ha('center')
        
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        ax.set_ylim(bottom=0)
        ax.set_xlim(grouped_data['time_group'].min() - pd.Timedelta(days=0.5), grouped_data['time_group'].max() + pd.Timedelta(days=0.5))
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        return encoded_image
    return ""

def generate_harvested_benches_week_chart(data, period):
    if not data.empty and period == 'week':
        data['time_group'] = data['crate weight timestamp'].dt.floor('D')
        grouped_data = data.groupby('time_group').size().reset_index(name='counts')
        
        fig, ax = plt.subplots()
        grouped_data = grouped_data.sort_values('time_group')
        
        ax.bar(
            grouped_data['time_group'],
            grouped_data['counts'],
            width=1.0,
            color='#00637A',
            edgecolor='white',
            linewidth=0.5,
            align='center'
        )
        
        for x, y in zip(grouped_data['time_group'], grouped_data['counts']):
            ax.text(x, y / 2, f'{y}', ha='center', va='center', color='white', fontsize=10, weight='bold')
        
        ax.set_title('Harvested Benches versus Time')
        ax.set_xlabel('')
        ax.set_ylabel('Harvested Benches')
        
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
        for label in ax.get_xticklabels():
            label.set_ha('center')
        
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        ax.set_ylim(bottom=0)
        ax.set_xlim(grouped_data['time_group'].min() - pd.Timedelta(days=0.5), grouped_data['time_group'].max() + pd.Timedelta(days=0.5))
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        return encoded_image
    return ""

def generate_average_yield_week_chart(data, period):
    if not data.empty and period == 'week':
        data['time_group'] = data['crate weight timestamp'].dt.floor('D')
        grouped_data = data.groupby('time_group').agg(
            total_weight=('weight in kilograms', 'sum'),
            total_benches=('crate weight timestamp', 'count')
        ).reset_index()
        
        grouped_data['average_yield'] = grouped_data['total_weight'] / grouped_data['total_benches']
        
        fig, ax = plt.subplots()
        grouped_data = grouped_data.sort_values('time_group')
        
        ax.bar(
            grouped_data['time_group'],
            grouped_data['average_yield'],
            width=1.0,
            color='#00637A',
            edgecolor='white',
            linewidth=0.5,
            align='center'
        )
        
        for x, y in zip(grouped_data['time_group'], grouped_data['average_yield']):
            ax.text(x, y / 2, f'{y:.2f}', ha='center', va='center', color='white', fontsize=10, weight='bold')
        
        ax.set_title('Average Yield per Day')
        ax.set_xlabel('')
        ax.set_ylabel('Average Yield (KG/Bench)')
        
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
        for label in ax.get_xticklabels():
            label.set_ha('center')
        
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        ax.set_ylim(bottom=0)
        ax.set_xlim(grouped_data['time_group'].min() - pd.Timedelta(days=0.5), grouped_data['time_group'].max() + pd.Timedelta(days=0.5))
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        return encoded_image
    return ""