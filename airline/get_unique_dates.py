#!/usr/bin/env python3
"""
Extract all unique departure dates from booking requests CSV.

Usage:
    python get_unique_dates.py [csv_file]
    
Example:
    python get_unique_dates.py
    python get_unique_dates.py booking_requests_simplified.csv
"""

import csv
import sys


def get_unique_dates(csv_file):
    """Extract all unique departure dates from CSV file"""
    dates = set()
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.add(row['departure_date'])
    
    return sorted(dates)


def main():
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'booking_requests_simplified.csv'
    
    # Check if file exists
    try:
        with open(csv_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found: {csv_file}", file=sys.stderr)
        sys.exit(1)
    
    # Get unique dates
    dates = get_unique_dates(csv_file)
    
    # Print one date per line
    for date in dates:
        print(date)


if __name__ == '__main__':
    main()
