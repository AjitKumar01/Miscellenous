#!/usr/bin/env python3
"""
Generate plots for WTP and Booking Demand analysis.

Usage:
    python plot_analysis.py <departure_date> [csv_file]
    
Example:
    python plot_analysis.py 2012-Apr-30
    python plot_analysis.py 2012-Apr-30 booking_requests_simplified.csv
    
Generates two plots:
    1. wtp_vs_dtd_<date>.png - Mean WTP against Days to Departure
    2. cumulative_bookings_vs_dtd_<date>.png - Cumulative bookings against DTD
"""

import csv
import sys
from collections import defaultdict
import matplotlib.pyplot as plt


def analyze_data(csv_file, target_date):
    """
    Analyze WTP and booking demand by DTD for a specific flight date.
    
    Returns:
        Tuple of (wtp_by_dtd, demand_by_dtd)
    """
    wtp_by_dtd = defaultdict(list)
    demand_by_dtd = defaultdict(int)
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if row['departure_date'] == target_date:
                dtd = int(row['days_to_departure'])
                wtp = float(row['wtp'])
                
                wtp_by_dtd[dtd].append(wtp)
                demand_by_dtd[dtd] += 1
    
    # Calculate mean WTP for each DTD
    mean_wtp = {}
    for dtd, wtp_values in wtp_by_dtd.items():
        mean_wtp[dtd] = sum(wtp_values) / len(wtp_values)
    
    return mean_wtp, demand_by_dtd


def plot_wtp_vs_dtd(mean_wtp, target_date):
    """Generate WTP vs DTD plot"""
    if not mean_wtp:
        print(f"No data to plot for {target_date}")
        return
    
    dtd_values = sorted(mean_wtp.keys())
    wtp_values = [mean_wtp[dtd] for dtd in dtd_values]
    
    plt.figure(figsize=(12, 6))
    plt.plot(dtd_values, wtp_values, 'o-', linewidth=2, markersize=4, alpha=0.7)
    plt.xlabel('Days to Departure (DTD)', fontsize=12)
    plt.ylabel('Mean Willingness to Pay (EUR)', fontsize=12)
    plt.title(f'Mean WTP vs Days to Departure\nFlight Date: {target_date}', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    filename = f'wtp_vs_dtd_{target_date}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Created: {filename}")
    plt.close()


def plot_cumulative_bookings(demand_by_dtd, target_date):
    """Generate cumulative bookings vs DTD plot"""
    if not demand_by_dtd:
        print(f"No data to plot for {target_date}")
        return
    
    # Calculate cumulative bookings from highest DTD (earliest) to 0 (departure)
    dtd_values = sorted(demand_by_dtd.keys())
    cumulative_dict = {}
    total = 0
    
    # Accumulate from highest DTD down to 0
    for dtd in sorted(demand_by_dtd.keys(), reverse=True):
        total += demand_by_dtd[dtd]
        cumulative_dict[dtd] = total
    
    # Get cumulative values in ascending DTD order for plotting
    cumulative = [cumulative_dict[dtd] for dtd in dtd_values]
    
    plt.figure(figsize=(12, 6))
    plt.plot(dtd_values, cumulative, 'o-', linewidth=2, markersize=4, color='#2E86AB', alpha=0.7)
    plt.fill_between(dtd_values, cumulative, alpha=0.3, color='#2E86AB')
    plt.xlabel('Days to Departure (DTD)', fontsize=12)
    plt.ylabel('Cumulative Number of Bookings', fontsize=12)
    plt.title(f'Cumulative Bookings vs Days to Departure\nFlight Date: {target_date}', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Add total bookings annotation (without arrow)
    plt.text(dtd_values[-1]*0.7, total*0.95, f'Total: {total} bookings', 
             fontsize=11,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    
    filename = f'cumulative_bookings_vs_dtd_{target_date}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Created: {filename}")
    plt.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_analysis.py <departure_date> [csv_file]")
        print()
        print("Example:")
        print("  python plot_analysis.py 2012-Apr-30")
        print("  python plot_analysis.py 2012-Apr-30 booking_requests_simplified.csv")
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
    
    print(f"Analyzing data for flight date: {target_date}")
    print()
    
    # Analyze data
    mean_wtp, demand_by_dtd = analyze_data(csv_file, target_date)
    
    if not mean_wtp:
        print(f"❌ No booking requests found for departure date: {target_date}")
        sys.exit(1)
    
    # Generate plots
    print("Generating plots...")
    plot_wtp_vs_dtd(mean_wtp, target_date)
    plot_cumulative_bookings(demand_by_dtd, target_date)
    print()
    print("✓ Done!")


if __name__ == '__main__':
    main()
