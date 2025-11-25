#!/usr/bin/env python3
"""
Extract complete booking request data from tvlsim.log including:
- Request details
- Solution provided (fare options offered)
- Customer choice (chosen fare option)
- Inventory status after booking
"""

import re
import csv
from collections import defaultdict
from datetime import datetime


def parse_booking_request(line):
    """
    Parse booking request line.
    
    Format: At 2009-Mar-13 01:54:26.501000, for (SIN, IN) SIN-BKK (RO) 2009-Apr-20 (1 days) 18:28:13 Y 1 N 455.203 31.7392 0 50 1 50
    
    Fields:
    - Request timestamp
    - POS, Customer type
    - Origin-Destination
    - Trip type (RO/OW/RI)
    - Departure date
    - Stay duration (number of days for the trip)
    - Request time
    - Preferred cabin
    - Party size
    - Frequent flyer status (G/S/M/N)
    - WTP (Willingness to Pay)
    - Value of time
    - Change fees
    - Non-refundable
    - Preferences
    """
    
    # Pattern: Now captures departure_time (group 9) and disutility fields (groups 16, 18)
    # Format: At <timestamp>, for (<pos>, <channel>) <origin>-<dest> (<trip_type>) <dep_date> (<stay_duration> days) <dep_time> <cabin> <party> <ff> <wtp> <vot> <cf> <cfd> <nr> <nrd>
    pattern = r'At (\S+ \S+), for \((\S+), (\S+)\) (\S+)-(\S+) \((\S+)\) (\S+) \((\d+) days\) (\S+) (\S) (\d+) (\S) ([\d.]+) ([\d.]+) (\d+) (\d+) (\d+) (\d+)'
    
    match = re.search(pattern, line)
    if match:
        from datetime import datetime
        
        # Parse dates to calculate actual DTD
        request_ts = match.group(1)
        departure_date = match.group(7)
        
        try:
            req_dt = datetime.strptime(request_ts, '%Y-%b-%d %H:%M:%S.%f')
            dep_dt = datetime.strptime(departure_date, '%Y-%b-%d')
            days_to_departure = (dep_dt - req_dt).days
        except:
            days_to_departure = None
        
        return {
            'request_timestamp': request_ts,
            'pos': match.group(2),
            'channel': match.group(3),  # FIXED: was "customer_type", now correct
            'origin': match.group(4),
            'destination': match.group(5),
            'trip_type': match.group(6),
            'departure_date': departure_date,
            'stay_duration': int(match.group(8)),  # CORRECTED: This is stay duration, not DTD
            'days_to_departure': days_to_departure,  # NEW: Calculated actual DTD
            'departure_time': match.group(9),  # NEW: Added departure time
            'cabin': match.group(10),
            'party_size': int(match.group(11)),
            'ff_status': match.group(12),
            'wtp': float(match.group(13)),
            'value_of_time': float(match.group(14)),
            'change_fees': int(match.group(15)),
            'change_fee_disutility': int(match.group(16)),  # NEW: Added disutility
            'non_refundable': int(match.group(17)),
            'non_refundable_disutility': int(match.group(18))  # NEW: Added disutility
        }
    return None


def parse_fare_options(lines, start_idx, direction='forward'):
    """
    Parse fare options provided to the customer.
    
    Format: A corresponding fare option for the 'SQ Y' class is: Class path: Y; 400 EUR; conditions: 0 0 0
    """
    fare_options = []
    
    # Determine search range
    if direction == 'forward':
        search_range = range(start_idx, min(start_idx + 50, len(lines)))
    else:  # backward
        search_range = range(max(0, start_idx - 50), start_idx)
    
    # Look for fare option lines
    for i in search_range:
        line = lines[i]
            
        # Parse fare option from FareQuoter output
        # Pattern: A corresponding fare option for the 'SQ X' class is: Class path: X; ### EUR; conditions: # # #
        match = re.search(r"A corresponding fare option for the '[A-Z]+ ([A-Z])' class is: Class path: ([A-Z]); ([\d.]+) EUR; conditions: (\d+) (\d+) (\d+)", line)
        if match:
            fare_options.append({
                'class': match.group(2),
                'fare': float(match.group(3)),
                'change_fee_cond': int(match.group(4)),
                'non_refundable_cond': int(match.group(5)),
                'saturday_stay_cond': int(match.group(6))
            })
    
    # Convert list to dict with concatenated strings
    if fare_options:
        return {
            'offered_classes': ','.join([opt['class'] for opt in fare_options]),
            'offered_fares': ','.join([str(opt['fare']) for opt in fare_options]),
            'offered_change_fees': ','.join([str(opt['change_fee_cond']) for opt in fare_options]),
            'offered_non_refundable': ','.join([str(opt['non_refundable_cond']) for opt in fare_options]),
            'offered_saturday_stay': ','.join([str(opt['saturday_stay_cond']) for opt in fare_options])
        }
    
    return {}


def parse_availability(lines, start_idx, direction='forward'):
    """
    Parse availability for each fare class.
    
    Format: Fare option Class path: Y; 400 EUR; conditions: 0 0 0, Availability 16, Segment Path ...
    """
    availability = {}
    
    # Determine search range
    if direction == 'forward':
        search_range = range(start_idx, min(start_idx + 50, len(lines)))
    else:  # backward
        search_range = range(max(0, start_idx - 50), start_idx)
    
    # Look for availability lines
    for i in search_range:
        line = lines[i]
            
        # Parse availability from InventoryManager output
        match = re.search(r"Fare option Class path: ([A-Z]);.*Availability (\d+)", line)
        if match:
            availability[match.group(1)] = int(match.group(2))
    
    return availability


def parse_chosen_solution(line):
    """
    Parse the chosen travel solution (customer choice).
    
    Format: Chosen TS: Segment path: SQ; 12, 2012-Apr-30; SIN, BKK; 08:20:00 ### Chosen fare option: Class path: M; 160 EUR; conditions: 1 1 1 ## Among: ...
    """
    result = {}
    
    # Parse segment path (airline and flight number)
    segment_match = re.search(r"Segment path: ([A-Z]+); (\d+),", line)
    if segment_match:
        result['airline'] = segment_match.group(1)
        result['flight_number'] = segment_match.group(2)
    
    # Parse chosen fare option
    fare_match = re.search(r"Chosen fare option: Class path: ([A-Z]); ([\d.]+) EUR; conditions: (\d+) (\d+) (\d+)", line)
    if fare_match:
        result.update({
            'chosen_class': fare_match.group(1),
            'chosen_fare': float(fare_match.group(2)),
            'chosen_change_fee': int(fare_match.group(3)),
            'chosen_non_refundable': int(fare_match.group(4)),
            'chosen_saturday_stay': int(fare_match.group(5))
        })
    
    return result if result else None


def parse_sale_confirmation(line):
    """
    Parse sale confirmation line.
    
    Format: Made a sell of 1 persons on the following travel solution: ... Successful? 1
    """
    
    match = re.search(r"Made a sell of (\d+) persons.*Successful\? ([01])", line)
    if match:
        return {
            'sold_party_size': int(match.group(1)),
            'sale_successful': bool(int(match.group(2)))
        }
    return None


def extract_complete_booking_data(log_file='logs/tvlsim.log'):
    """
    Extract complete booking request data from log file.
    """
    
    print(f"Reading {log_file}...")
    
    # Read all lines into memory for lookahead
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    print(f"✓ Loaded {len(lines):,} lines")
    
    bookings = []
    current_request = None
    current_fare_options = None
    current_availability = None
    
    for i, line in enumerate(lines):
        # Parse booking request
        if 'Poped booking request:' in line:
            request = parse_booking_request(line)
            if request:
                current_request = request
                current_request['request_id'] = len(bookings) + 1
                current_request['line_number'] = i + 1
                
                # Initialize with defaults (will be updated when we find choice/denial)
                current_request['offered_classes'] = ''
                current_request['offered_fares'] = ''
                
                # Add availability defaults
                for cls in ['Y', 'B', 'M']:
                    current_request[f'availability_{cls}_before'] = 0
                
                # Default values for choice (will be updated if chosen)
                current_request['customer_chose'] = False
                current_request['chosen_class'] = None
                current_request['chosen_fare'] = None
                current_request['sale_successful'] = False
        
        # Parse chosen solution (customer choice)
        elif 'Chosen TS:' in line and current_request:
            choice = parse_chosen_solution(line)
            if choice:
                current_request['customer_chose'] = True
                current_request['airline'] = choice.get('airline', '')
                current_request['flight_number'] = choice.get('flight_number', '')
                current_request['chosen_class'] = choice.get('chosen_class', '')
                current_request['chosen_fare'] = choice.get('chosen_fare', 0.0)
                current_request['chosen_change_fee'] = choice.get('chosen_change_fee', '')
                current_request['chosen_non_refundable'] = choice.get('chosen_non_refundable', '')
                current_request['chosen_saturday_stay'] = choice.get('chosen_saturday_stay', '')
                
                # Look backward for fare options and availability (they appear before the choice)
                fare_options_data = parse_fare_options(lines, i, direction='backward')
                current_availability = parse_availability(lines, i, direction='backward')
                
                # Update with parsed fare option data (includes classes, fares, and all conditions)
                if fare_options_data:
                    current_request.update(fare_options_data)
                
                # Update availability
                for cls in ['Y', 'B', 'M']:
                    current_request[f'availability_{cls}_before'] = current_availability.get(cls, 0) if current_availability else 0
        
        # Parse sale confirmation
        elif 'Made a sell of' in line and current_request:
            sale = parse_sale_confirmation(line)
            if sale:
                current_request['sale_successful'] = sale['sale_successful']
                current_request['sold_party_size'] = sale['sold_party_size']
                
                # Booking complete - save it
                bookings.append(current_request)
                current_request = None
        
        # Parse no choice (denied booking)
        elif 'There is no chosen travel solution' in line and current_request:
            current_request['customer_chose'] = False
            current_request['chosen_class'] = 'DENIED'
            current_request['chosen_fare'] = 0.0
            current_request['sale_successful'] = False
            
            # Booking complete - save it
            bookings.append(current_request)
            current_request = None
    
    print(f"✓ Extracted {len(bookings):,} booking requests")
    
    return bookings


def write_complete_csv(bookings, filename='booking_requests_complete.csv'):
    """
    Write complete booking data to CSV.
    """
    
    if not bookings:
        print("No bookings to write")
        return
    
    with open(filename, 'w', newline='') as f:
        # Define column order
        fieldnames = [
            'request_id',
            'line_number',
            'request_timestamp',
            'departure_date',
            'days_to_departure',
            'stay_duration',
            'departure_time',  # NEW: Added departure time
            'origin',
            'destination',
            'airline',  # NEW: Airline carrier code (e.g., SQ)
            'flight_number',  # NEW: Flight number
            'trip_type',
            'pos',
            'channel',  # FIXED: was "customer_type"
            'cabin',
            'party_size',
            'ff_status',
            'wtp',
            'value_of_time',
            'change_fees',
            'change_fee_disutility',  # NEW: Added disutility
            'non_refundable',
            'non_refundable_disutility',  # NEW: Added disutility
            'offered_classes',
            'offered_fares',
            'offered_change_fees',  # NEW: Change fee conditions per class
            'offered_non_refundable',  # NEW: Non-refundable conditions per class
            'offered_saturday_stay',  # NEW: Saturday stay conditions per class
            'availability_Y_before',
            'availability_B_before',
            'availability_M_before',
            'customer_chose',
            'chosen_class',
            'chosen_fare',
            'chosen_change_fee',
            'chosen_non_refundable',
            'chosen_saturday_stay',  # NEW: Saturday stay condition for chosen option
            'sale_successful',
            'sold_party_size'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for booking in bookings:
            writer.writerow(booking)
    
    print(f"✓ Written: {filename} ({len(bookings):,} rows)")


def write_summary_stats(bookings, filename='booking_summary_stats.txt'):
    """
    Write summary statistics.
    """
    
    total_requests = len(bookings)
    customer_chose = sum(1 for b in bookings if b['customer_chose'])
    customer_denied = sum(1 for b in bookings if b['chosen_class'] == 'DENIED')
    successful_sales = sum(1 for b in bookings if b['sale_successful'])
    
    # Choice analysis
    chosen_classes = defaultdict(int)
    for b in bookings:
        if b['customer_chose'] and b['chosen_class'] != 'DENIED':
            chosen_classes[b['chosen_class']] += 1
    
    # Availability analysis
    avg_availability = {
        'Y': sum(b['availability_Y_before'] for b in bookings) / total_requests,
        'B': sum(b['availability_B_before'] for b in bookings) / total_requests,
        'M': sum(b['availability_M_before'] for b in bookings) / total_requests
    }
    
    with open(filename, 'w') as f:
        f.write("="*70 + "\n")
        f.write(" BOOKING REQUESTS ANALYSIS\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Total Booking Requests: {total_requests:,}\n")
        f.write(f"Customer Made Choice: {customer_chose:,} ({customer_chose/total_requests*100:.1f}%)\n")
        f.write(f"Customer Denied (No Options): {customer_denied:,} ({customer_denied/total_requests*100:.1f}%)\n")
        f.write(f"Successful Sales: {successful_sales:,} ({successful_sales/total_requests*100:.1f}%)\n\n")
        
        f.write("Chosen Class Distribution:\n")
        for cls in sorted(chosen_classes.keys()):
            count = chosen_classes[cls]
            pct = (count / customer_chose * 100) if customer_chose > 0 else 0
            f.write(f"  Class {cls}: {count:>6,} ({pct:>5.1f}%)\n")
        
        f.write("\nAverage Availability (Before Booking):\n")
        for cls in ['Y', 'B', 'M']:
            f.write(f"  Class {cls}: {avg_availability[cls]:.2f} seats\n")
        
        f.write("\n" + "="*70 + "\n")
    
    print(f"✓ Written: {filename}")


def print_sample_records(bookings, n=5):
    """
    Print sample records for verification.
    """
    
    print("\n" + "="*70)
    print(f" SAMPLE RECORDS (first {n})")
    print("="*70)
    
    for i, booking in enumerate(bookings[:n], 1):
        print(f"\nRequest #{i}:")
        print(f"  Timestamp: {booking['request_timestamp']}")
        print(f"  Route: {booking['origin']}-{booking['destination']} ({booking['trip_type']})")
        print(f"  Departure: {booking['departure_date']} (DTD={booking['days_to_departure']} days)")
        print(f"  Stay Duration: {booking['stay_duration']} days")
        print(f"  Channel: {booking['channel']}, FF={booking['ff_status']}, WTP={booking['wtp']:.2f}")
        print(f"  Offered: {booking['offered_classes']} @ {booking['offered_fares']} EUR")
        print(f"  Availability: Y={booking['availability_Y_before']}, B={booking['availability_B_before']}, M={booking['availability_M_before']}")
        print(f"  Chose: {booking['chosen_class']} @ {booking.get('chosen_fare', 0):.2f} EUR")
        print(f"  Sale: {'SUCCESS' if booking['sale_successful'] else 'FAILED/DENIED'}")


def main():
    """
    Main execution.
    """
    
    import sys
    
    # Get log file from command line or use default
    log_file = sys.argv[1] if len(sys.argv) > 1 else 'logs/tvlsim.log'
    
    print("="*70)
    print(" COMPLETE BOOKING REQUEST EXTRACTION")
    print("="*70)
    print(f"\nLog file: {log_file}\n")
    
    # Extract data
    bookings = extract_complete_booking_data(log_file)
    
    if not bookings:
        print("\nNo bookings found!")
        return
    
    # Write outputs
    write_complete_csv(bookings)
    write_summary_stats(bookings)
    
    # Print samples
    print_sample_records(bookings)
    
    print("\n" + "="*70)
    print(" EXTRACTION COMPLETE")
    print("="*70)
    print("""
Files created:
  1. booking_requests_complete.csv - Full detailed data
  2. booking_summary_stats.txt - Summary statistics

CSV Columns:
  - Request info: timestamp, route, departure date, DTD, customer details
  - Offered solutions: classes, fares, availability before booking
  - Customer choice: chosen class, fare, conditions
  - Sale result: success/failure, inventory status after

Use this data for:
  - Choice modeling (what customers selected)
  - Demand analysis (requests vs acceptances)
  - Revenue optimization (fare class mix)
  - Inventory analysis (availability patterns)
""")


if __name__ == "__main__":
    main()
