#!/usr/bin/env python3
"""
Analyze booking demand by Days to Departure (DTD) for a specific flight departure date.

Usage:
    python booking_demand_by_dtd.py <departure_date> [csv_file]
    
Example:
    python booking_demand_by_dtd.py 2012-Apr-30
    python booking_demand_by_dtd.py 2012-Apr-30 booking_requests_simplified.csv
"""

import csv
import sys
from collections import defaultdict
from datetime import datetime


def parse_date(date_str):
    """Parse date string in format like '2012-Apr-30'"""
    try:
        return datetime.strptime(date_str, '%Y-%b-%d')
    except ValueError:
        # Try alternative format
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None


def analyze_booking_demand(csv_file, target_date):
    """
    Analyze booking requests by days to departure for a specific flight date.
    
    Args:
        csv_file: Path to CSV file with booking data
        target_date: Target departure date to analyze
    
    Returns:
        Dictionary with DTD as keys and booking counts as values
    """
    demand_by_dtd = defaultdict(int)
    total_requests = 0
    successful_bookings = 0
    denied_bookings = 0
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Check if this booking is for our target date
            if row['departure_date'] == target_date:
                total_requests += 1
                dtd = int(row['days_to_departure'])
                demand_by_dtd[dtd] += 1
                
                # Count successful vs denied
                if row.get('sale_successful') == 'True':
                    successful_bookings += 1
                elif row.get('chosen_class') in ['DENIED', '']:
                    denied_bookings += 1
    
    return {
        'demand_by_dtd': dict(sorted(demand_by_dtd.items())),
        'total_requests': total_requests,
        'successful_bookings': successful_bookings,
        'denied_bookings': denied_bookings
    }


def print_demand_analysis(target_date, results):
    """Print raw demand data by DTD"""
    demand_by_dtd = results['demand_by_dtd']
    total = results['total_requests']
    
    if total == 0:
        print(f"❌ No booking requests found for departure date: {target_date}")
        print()
        return
    
    print("days_to_departure,booking_requests,cumulative_requests")
    
    # Calculate cumulative from highest DTD (earliest) to 0 (departure)
    cumulative = 0
    for dtd in sorted(demand_by_dtd.keys(), reverse=True):
        cumulative += demand_by_dtd[dtd]
        # Store for later printing in ascending order
    
    # Print in ascending DTD order with correct cumulative
    cumulative = 0
    sorted_dtds = sorted(demand_by_dtd.keys(), reverse=True)
    cumulative_values = {}
    
    for dtd in sorted_dtds:
        cumulative += demand_by_dtd[dtd]
        cumulative_values[dtd] = cumulative
    
    # Print in ascending order
    for dtd in sorted(demand_by_dtd.keys()):
        print(f"{dtd},{demand_by_dtd[dtd]},{cumulative_values[dtd]}")


def show_available_dates(csv_file, limit=20):
    """Show available departure dates in the CSV file"""
    dates = set()
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dates.add(row['departure_date'])
    
    sorted_dates = sorted(dates)
    
    print("=" * 80)
    print(f" AVAILABLE DEPARTURE DATES (showing first {limit})")
    print("=" * 80)
    print()
    
    for i, date in enumerate(sorted_dates[:limit], 1):
        print(f"  {i:2}. {date}")
    
    if len(sorted_dates) > limit:
        print(f"  ... and {len(sorted_dates) - limit} more dates")
    
    print()
    print(f"Total unique departure dates: {len(sorted_dates)}")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python booking_demand_by_dtd.py <departure_date> [csv_file]")
        print()
        print("Example:")
        print("  python booking_demand_by_dtd.py 2012-Apr-30")
        print("  python booking_demand_by_dtd.py 2012-Apr-30 booking_requests_simplified.csv")
        print()
        sys.exit(1)
    
    target_date = sys.argv[1]
    csv_file = sys.argv[2] if len(sys.argv) > 2 else 'booking_requests_simplified.csv'
    
    # Check if file exists
    try:
        with open(csv_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found: {csv_file}")
        print()
        print("Available files:")
        print("  - booking_requests_complete.csv")
        print("  - booking_requests_simplified.csv")
        sys.exit(1)
    
    # If user wants to see available dates
    if target_date.lower() in ['list', 'show', 'dates']:
        show_available_dates(csv_file)
        sys.exit(0)
    
    # Analyze demand
    results = analyze_booking_demand(csv_file, target_date)
    
    # Print results
    print_demand_analysis(target_date, results)
    
    # If no data found, show available dates
    if results['total_requests'] == 0:
        show_available_dates(csv_file, limit=10)


if __name__ == '__main__':
    main()
