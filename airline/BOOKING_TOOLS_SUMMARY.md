# 📦 TvlSim Booking Data Extraction - Complete Package

## ✨ What's Included

You now have a complete set of tools to extract, analyze, and visualize booking data from your TvlSim simulations for demand forecasting!

### 📁 Files Created

1. **`extract_bookings.py`** - Main extraction script (Python)
   - Parses simulation logs
   - Extracts booking data
   - Exports to CSV, JSON, and demand forecast formats

2. **`analyze_bookings.sh`** - Automated extraction wrapper (Bash)
   - One-command solution
   - Analyzes log file
   - Generates all output formats
   - Shows summary statistics

3. **`visualize_bookings.py`** - Data visualization script (Python)
   - Creates charts and graphs
   - Generates visual analysis
   - Produces text summaries

4. **`quickstart_bookings.sh`** - Interactive quick start guide
   - Checks your setup
   - Guides you through the process
   - Offers to run extraction automatically

5. **`BOOKING_EXTRACTION_README.md`** - Complete documentation
   - Detailed usage instructions
   - Examples for demand forecasting
   - Python/R code examples
   - Troubleshooting guide

---

## 🚀 Quick Start (3 Simple Steps)

### Step 1: Run Your Simulation

If you haven't already:

```bash
# Option A: Interactive mode
./tvlsim/tvlsim -b
> simulate
> quit

# Option B: Batch mode
simulate
```

This creates `simulate.log` with all booking data.

### Step 2: Extract the Data

**Easiest way:**
```bash
./analyze_bookings.sh
```

**Or use Python directly:**
```bash
python3 extract_bookings.py --log simulate.log --csv bookings.csv
```

### Step 3: Use the Data

The extracted files are ready for demand forecasting!

```bash
# View the data
head booking_data_*/demand_forecast.csv

# Load in Python
python3 -c "import pandas as pd; df = pd.read_csv('booking_data_*/demand_forecast.csv'); print(df.head())"

# Visualize
python3 visualize_bookings.py booking_data_*/demand_forecast.csv
```

---

## 📊 Output Files Explained

### For Demand Forecasting → Use `demand_forecast.csv`

This is your main file for forecasting! It contains:

- **Aggregated bookings** by date, route, and cabin
- **Passenger counts** for capacity planning
- **Average willingness-to-pay** for pricing
- **Booking lead times** for timing analysis
- **Demand levels** (HIGH/MEDIUM/LOW) for classification

### For Detailed Analysis → Use `bookings_raw.csv`

Contains every individual booking with:
- Complete request details
- Flight paths chosen
- Timestamps
- All available fields

### For APIs/Integration → Use `bookings_full.json`

Structured JSON with:
- All booking data
- Metadata
- Statistics
- Easy to parse programmatically

---

## 💡 Common Use Cases

### 1. **Build a Demand Forecasting Model**

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Load data
df = pd.read_csv('booking_data_*/demand_forecast.csv')

# Prepare features
X = pd.get_dummies(df[['origin', 'destination', 'cabin', 'avg_booking_lead_time']])
y = df['booking_count']

# Split and train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor()
model.fit(X_train, y_train)

print(f"Model Score: {model.score(X_test, y_test):.2f}")
```

### 2. **Analyze Route Performance**

```python
import pandas as pd

df = pd.read_csv('booking_data_*/demand_forecast.csv')

# Top performing routes
top_routes = df.groupby(['origin', 'destination']).agg({
    'booking_count': 'sum',
    'total_passengers': 'sum',
    'avg_wtp': 'mean'
}).sort_values('booking_count', ascending=False)

print(top_routes.head(10))
```

### 3. **Study Booking Patterns**

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('booking_data_*/bookings_raw.csv')

# Lead time analysis
df['days_to_departure'].hist(bins=50)
plt.title('When Do Passengers Book?')
plt.xlabel('Days Before Departure')
plt.ylabel('Number of Bookings')
plt.show()
```

### 4. **Revenue Management Analysis**

```python
import pandas as pd

df = pd.read_csv('booking_data_*/demand_forecast.csv')

# WTP by lead time
df_sorted = df.sort_values('avg_booking_lead_time')
plt.plot(df_sorted['avg_booking_lead_time'], df_sorted['avg_wtp'])
plt.title('WTP vs Booking Lead Time')
plt.xlabel('Days Before Departure')
plt.ylabel('Willingness to Pay ($)')
plt.show()
```

---

## 🎯 Next Steps

1. **Run your simulation** if you haven't already
2. **Extract the data** using `./analyze_bookings.sh`
3. **Explore the output** files
4. **Build your forecasting model** using the provided examples
5. **Iterate** - Run more simulations with different parameters

---

## 📞 Need Help?

### Check the log extraction worked:
```bash
wc -l booking_data_*/bookings_raw.csv
# Should show number of bookings extracted
```

### View sample data:
```bash
head -20 booking_data_*/demand_forecast.csv | column -t -s,
```

### Common issues:

**"No bookings found"**
- Check simulation actually ran: `tail simulate.log`
- Verify bookings in log: `grep -i booking simulate.log | head`

**"Python module not found"**
```bash
# Install required packages
pip3 install pandas matplotlib seaborn
```

**"Permission denied"**
```bash
chmod +x *.sh *.py
```

---

## 📚 Additional Resources

- **Full Documentation**: `BOOKING_EXTRACTION_README.md`
- **TvlSim Main README**: `README.md`
- **Python Help**: `python3 extract_bookings.py --help`
- **Quick Start**: `./quickstart_bookings.sh`

---

## ✅ Summary

You now have:

✓ Scripts to extract booking data from logs
✓ Multiple output formats (CSV, JSON)
✓ Demand forecast aggregated data
✓ Visualization tools
✓ Example code for forecasting
✓ Complete documentation

**Ready to use for demand forecasting, revenue management analysis, and market research!**

---

*Generated for TvlSim v1.01.9*
