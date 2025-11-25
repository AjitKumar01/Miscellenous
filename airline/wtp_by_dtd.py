#!/usr/bin/env python3
"""
Analyze Willingness to Pay (WTP) by Days to Departure (DTD) for a specific flight departure date.

Usage:
    python wtp_by_dtd.py <departure_date> [csv_file]
    
Example:
    python wtp_by_dtd.py 2012-Apr-30
    python wtp_by_dtd.py 2012-Apr-30 booking_requests_simplified.csv
"""

import csv
import sys
from collections import defaultdict


def analyze_wtp_by_dtd(csv_file, target_date):
    """
    Analyze WTP by days to departure for a specific flight date.
    
    Args:
        csv_file: Path to CSV file with booking data
        target_date: Target departure date to analyze
    
    Returns:
        Dictionary with DTD as keys and WTP statistics as values
    """
    wtp_by_dtd = defaultdict(list)
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Check if this booking is for our target date
            if row['departure_date'] == target_date:
                dtd = int(row['days_to_departure'])
                wtp = float(row['wtp'])
                wtp_by_dtd[dtd].append(wtp)
    
    # Calculate statistics for each DTD
    wtp_stats = {}
    for dtd, wtp_values in sorted(wtp_by_dtd.items()):
        wtp_stats[dtd] = {
            'count': len(wtp_values),
            'mean': sum(wtp_values) / len(wtp_values),
            'min': min(wtp_values),
            'max': max(wtp_values),
            'median': sorted(wtp_values)[len(wtp_values)//2]
        }
    
    return wtp_stats


def print_wtp_analysis(target_date, wtp_stats):
    """Print WTP statistics by DTD in CSV format"""
    
    if not wtp_stats:
        print(f"❌ No booking requests found for departure date: {target_date}")
        return
    
    print("days_to_departure,booking_requests,mean_wtp,min_wtp,max_wtp,median_wtp")
    
    for dtd in sorted(wtp_stats.keys()):
        stats = wtp_stats[dtd]
        print(f"{dtd},{stats['count']},{stats['mean']:.2f},{stats['min']:.2f},{stats['max']:.2f},{stats['median']:.2f}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python wtp_by_dtd.py <departure_date> [csv_file]")
        print()
        print("Example:")
        print("  python wtp_by_dtd.py 2012-Apr-30")
        print("  python wtp_by_dtd.py 2012-Apr-30 booking_requests_simplified.csv")
        sys.exit(1)
    
    target_date = sys.argv[1]
    csv_file = sys.argv[2] if len(sys.argv) > 2 else 'booking_requests_simplified.csv'
    
    # Check if file exists
    try:
        with open(csv_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found: {csv_file}")
        sys.exit(1)
    
    # Analyze WTP
    wtp_stats = analyze_wtp_by_dtd(csv_file, target_date)
    
    # Print results
    print_wtp_analysis(target_date, wtp_stats)


if __name__ == '__main__':
    main()
