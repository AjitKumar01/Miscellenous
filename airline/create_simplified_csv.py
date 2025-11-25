#!/usr/bin/env python3
"""
Create a simplified version of booking_requests_complete.csv by dropping offered option columns.

Drops these columns:
    - offered_classes
    - offered_fares
    - offered_change_fees
    - offered_non_refundable
    - offered_saturday_stay

Usage:
    python create_simplified_csv.py [input_csv] [output_csv]
    
Example:
    python create_simplified_csv.py
    python create_simplified_csv.py booking_requests_complete.csv booking_requests_simplified.csv
"""

import csv
import sys


def create_simplified_csv(input_file, output_file):
    """Create simplified CSV by dropping offered option columns"""
    
    # Columns to drop
    columns_to_drop = [
        'offered_classes',
        'offered_fares', 
        'offered_change_fees',
        'offered_non_refundable',
        'offered_saturday_stay'
    ]
    
    # Read the complete CSV
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        # Create new fieldnames list without dropped columns
        new_fieldnames = [col for col in fieldnames if col not in columns_to_drop]
        
        # Read all rows
        rows = list(reader)
        
        # Write to new CSV file
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=new_fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
    
    return len(rows), len(fieldnames), len(new_fieldnames)


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'booking_requests_complete.csv'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'booking_requests_simplified.csv'
    
    # Check if input file exists
    try:
        with open(input_file, 'r') as f:
            pass
    except FileNotFoundError:
        print(f"❌ Error: Input file not found: {input_file}")
        sys.exit(1)
    
    print(f"Creating simplified CSV...")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
    print()
    
    # Create simplified CSV
    rows, orig_cols, new_cols = create_simplified_csv(input_file, output_file)
    
    print(f"✓ Created: {output_file}")
    print(f"  Rows: {rows:,}")
    print(f"  Original columns: {orig_cols}")
    print(f"  New columns: {new_cols}")
    print(f"  Dropped: {orig_cols - new_cols} columns")


if __name__ == '__main__':
    main()
