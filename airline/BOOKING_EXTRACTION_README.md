# TvlSim Booking Data Extraction Tools

This directory contains tools to extract structured booking data from TvlSim simulation logs for use in demand forecasting and analysis.

## 📋 Overview

After running a TvlSim simulation, booking data is written to log files (typically `simulate.log`). These tools parse those logs and generate clean, structured data files suitable for:

- **Demand forecasting models**
- **Revenue management analysis**
- **Market research**
- **Machine learning training data**

## 🚀 Quick Start

### Option 1: Automated Analysis (Recommended)

```bash
# Make the script executable
chmod +x analyze_bookings.sh

# Run automated extraction and analysis
./analyze_bookings.sh
```

This will:
- Analyze your simulation log
- Extract all booking data
- Generate 3 output files (CSV, JSON, demand forecast format)
- Show summary statistics

### Option 2: Manual Python Script

```bash
# Basic usage - exports to bookings.csv
python3 extract_bookings.py --log simulate.log

# Export to multiple formats
python3 extract_bookings.py \
    --log simulate.log \
    --csv bookings_raw.csv \
    --json bookings_full.json \
    --demand demand_forecast.csv

# Just show statistics
python3 extract_bookings.py --log simulate.log --stats-only
```

## 📊 Output Formats

### 1. Raw Bookings CSV (`bookings_raw.csv`)
Complete booking records with all available fields:

| Field | Description |
|-------|-------------|
| `line_number` | Line number in log file |
| `timestamp` | Event timestamp |
| `status` | confirmed, requested, cancelled |
| `origin` | Origin airport (3-letter code) |
| `destination` | Destination airport |
| `preferred_departure_date` | Requested departure date |
| `request_date` | When booking was made |
| `party_size` | Number of passengers |
| `cabin` | Cabin class (Economy, Business, First) |
| `channel` | Booking channel |
| `wtp` | Willingness to pay |
| `flight_path` | Chosen flight segments |
| `days_to_departure` | Booking lead time |

**Use case**: Detailed analysis, individual booking patterns

### 2. Full JSON (`bookings_full.json`)
Complete data including metadata and statistics:

```json
{
  "metadata": {
    "source": "simulate.log",
    "extraction_date": "2025-11-15T10:30:00",
    "total_bookings": 1500
  },
  "bookings": [...],
  "statistics": {...}
}
```

**Use case**: Programmatic access, data pipelines, web APIs

### 3. Demand Forecast CSV (`demand_forecast.csv`)
Aggregated data by date, route, and cabin:

| Field | Description |
|-------|-------------|
| `departure_date` | Flight departure date |
| `origin` | Origin airport |
| `destination` | Destination airport |
| `cabin` | Cabin class |
| `booking_count` | Number of bookings |
| `total_passengers` | Total passenger count |
| `avg_wtp` | Average willingness to pay |
| `avg_booking_lead_time` | Average days before departure |
| `demand_level` | HIGH/MEDIUM/LOW classification |

**Use case**: Demand forecasting models, capacity planning, pricing optimization

## 📈 Using the Data for Demand Forecasting

### Python/Pandas Example

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load demand forecast data
df = pd.read_csv('booking_data_YYYYMMDD_HHMMSS/demand_forecast.csv')

# Analyze demand by route
route_demand = df.groupby(['origin', 'destination'])['booking_count'].sum()
print(route_demand.sort_values(ascending=False).head(10))

# Time series analysis
df['departure_date'] = pd.to_datetime(df['departure_date'])
daily_demand = df.groupby('departure_date')['total_passengers'].sum()
daily_demand.plot(title='Daily Passenger Demand')
plt.show()

# Lead time analysis
plt.hist(df['avg_booking_lead_time'], bins=30)
plt.xlabel('Days Before Departure')
plt.ylabel('Frequency')
plt.title('Booking Lead Time Distribution')
plt.show()
```

### R Example

```r
library(tidyverse)

# Load data
bookings <- read_csv('booking_data_YYYYMMDD_HHMMSS/bookings_raw.csv')

# Analyze by origin-destination
od_summary <- bookings %>%
  filter(status == 'confirmed') %>%
  group_by(origin, destination) %>%
  summarise(
    total_bookings = n(),
    avg_party_size = mean(party_size, na.rm = TRUE),
    avg_wtp = mean(wtp, na.rm = TRUE)
  ) %>%
  arrange(desc(total_bookings))

print(od_summary)

# Time series plot
bookings %>%
  filter(status == 'confirmed') %>%
  mutate(date = as.Date(preferred_departure_date)) %>%
  count(date) %>%
  ggplot(aes(x = date, y = n)) +
  geom_line() +
  labs(title = 'Daily Booking Volume', x = 'Date', y = 'Bookings')
```

### Machine Learning Features

The extracted data provides features for ML models:

```python
# Feature engineering example
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

df = pd.read_csv('booking_data_YYYYMMDD_HHMMSS/demand_forecast.csv')

# Create features
df['day_of_week'] = pd.to_datetime(df['departure_date']).dt.dayofweek
df['month'] = pd.to_datetime(df['departure_date']).dt.month
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

# One-hot encode categorical variables
df = pd.get_dummies(df, columns=['origin', 'destination', 'cabin'])

# Prepare training data
X = df.drop(['departure_date', 'booking_count', 'demand_level'], axis=1)
y = df['booking_count']

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(feature_importance.head(10))
```

## 🔧 Customizing the Extraction

### Modifying the Parser

Edit `extract_bookings.py` to add custom fields or parsing logic:

```python
def _parse_booking_request(self, line, line_num):
    # Add custom field extraction
    custom_pattern = r'CustomField:\s*(\w+)'
    custom_match = re.search(custom_pattern, line)
    if custom_match:
        booking['custom_field'] = custom_match.group(1)
```

### Filtering Data

```python
# Only export confirmed bookings
python3 extract_bookings.py --log simulate.log --csv confirmed_only.csv

# Then filter in your analysis:
df = pd.read_csv('bookings_raw.csv')
confirmed = df[df['status'] == 'confirmed']
confirmed.to_csv('confirmed_only.csv', index=False)
```

## 📚 Additional Examples

### Export to Database

```python
import pandas as pd
import sqlite3

# Read CSV
df = pd.read_csv('booking_data_YYYYMMDD_HHMMSS/bookings_raw.csv')

# Write to SQLite
conn = sqlite3.connect('bookings.db')
df.to_sql('bookings', conn, if_exists='replace', index=False)
conn.close()

# Query
conn = sqlite3.connect('bookings.db')
result = pd.read_sql_query("""
    SELECT origin, destination, COUNT(*) as bookings
    FROM bookings
    WHERE status = 'confirmed'
    GROUP BY origin, destination
    ORDER BY bookings DESC
    LIMIT 10
""", conn)
print(result)
```

### Generate Summary Report

```python
import pandas as pd
from datetime import datetime

df = pd.read_csv('booking_data_YYYYMMDD_HHMMSS/bookings_raw.csv')

# Generate HTML report
report = f"""
<html>
<head><title>Booking Analysis Report</title></head>
<body>
<h1>TvlSim Booking Analysis Report</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<h2>Summary Statistics</h2>
<ul>
<li>Total Bookings: {len(df)}</li>
<li>Confirmed: {len(df[df.status=='confirmed'])}</li>
<li>Average Party Size: {df.party_size.mean():.2f}</li>
</ul>

<h2>Top Routes</h2>
{df[df.status=='confirmed'].groupby(['origin','destination']).size().sort_values(ascending=False).head(10).to_frame('bookings').to_html()}
</body>
</html>
"""

with open('booking_report.html', 'w') as f:
    f.write(report)
```

## 🐛 Troubleshooting

### No bookings extracted?

1. Check log file exists: `ls -l simulate.log`
2. Verify log has booking data: `grep -i booking simulate.log | head`
3. Check file encoding: The script handles UTF-8 errors automatically
4. Try running with debug output: Add print statements to see what's being parsed

### Wrong format extracted?

- The parser looks for standard TvlSim log patterns
- If your log format is different, you may need to adjust the regex patterns in `extract_bookings.py`
- Check the `_parse_booking_request()` and `_parse_sale_notification()` methods

### Performance issues with large logs?

```bash
# Process in chunks for very large files (>1GB)
split -l 100000 simulate.log chunk_

# Process each chunk
for chunk in chunk_*; do
    python3 extract_bookings.py --log $chunk --csv "bookings_$chunk.csv"
done

# Merge results
cat bookings_chunk_*.csv > bookings_all.csv
```

## 📞 Support

For issues or questions:
- Check the TvlSim documentation
- Review the simulation log for errors
- Ensure the simulation completed successfully before extraction

## 📄 License

These tools are provided as part of the TvlSim project.
