#!/usr/bin/env python3
"""
TvlSim Booking Data Extractor
==============================
Extracts booking information from simulation log files and generates
structured data files for demand forecasting analysis.

Usage:
    python3 extract_bookings.py --log simulate.log --output bookings.csv
"""

import re
import csv
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
import sys


class BookingExtractor:
    """Extract and parse booking data from TvlSim simulation logs."""
    
    def __init__(self, log_file):
        self.log_file = log_file
        self.bookings = []
        self.statistics = defaultdict(int)
        
    def parse_log(self):
        """Parse the simulation log file and extract booking information."""
        print(f"📖 Reading log file: {self.log_file}")
        
        booking_count = 0
        cancellation_count = 0
        
        try:
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Extract booking requests
                    if 'booking request' in line.lower() or 'poped booking request' in line.lower():
                        booking_data = self._parse_booking_request(line, line_num)
                        if booking_data:
                            booking_count += 1
                            
                    # Extract successful bookings/sales (NOTIFICATION level)
                    elif 'NOTIFICATION' in line and ('/' in line or 'segment' in line.lower()):
                        sale_data = self._parse_sale_notification(line, line_num)
                        if sale_data:
                            self._merge_sale_with_booking(sale_data)
                            
                    # Extract cancellations
                    elif 'cancellation' in line.lower():
                        cancellation_count += 1
                        self.statistics['cancellations'] += 1
                        
                    # Progress indicator
                    if line_num % 10000 == 0:
                        print(f"  ... processed {line_num:,} lines")
                        
        except FileNotFoundError:
            print(f"❌ Error: Log file '{self.log_file}' not found!")
            sys.exit(1)
            
        print(f"✅ Parsing complete: {len(self.bookings)} bookings extracted")
        print(f"   - Booking requests: {booking_count}")
        print(f"   - Cancellations: {cancellation_count}")
        
    def _parse_booking_request(self, line, line_num):
        """Parse a booking request line from the log."""
        booking = {
            'line_number': line_num,
            'timestamp': self._extract_timestamp(line),
            'request_type': 'booking',
            'status': 'requested'
        }
        
        # Extract origin-destination
        od_pattern = r'Origin:\s*([A-Z]{3})[,\s]+Destination:\s*([A-Z]{3})'
        od_match = re.search(od_pattern, line)
        if od_match:
            booking['origin'] = od_match.group(1)
            booking['destination'] = od_match.group(2)
            
        # Extract dates
        date_pattern = r'(\d{4}-\w{3}-\d{2})'
        dates = re.findall(date_pattern, line)
        if dates:
            booking['preferred_departure_date'] = dates[0] if len(dates) > 0 else None
            booking['request_date'] = dates[1] if len(dates) > 1 else None
            
        # Extract party size
        party_pattern = r'Party[- ]?size:\s*(\d+)'
        party_match = re.search(party_pattern, line, re.IGNORECASE)
        if party_match:
            booking['party_size'] = int(party_match.group(1))
        
        # Extract cabin/class
        cabin_pattern = r'Cabin:\s*(\w+)'
        cabin_match = re.search(cabin_pattern, line, re.IGNORECASE)
        if cabin_match:
            booking['cabin'] = cabin_match.group(1)
            
        # Extract WTP (Willingness to Pay)
        wtp_pattern = r'WTP[:\s]+([0-9.]+)'
        wtp_match = re.search(wtp_pattern, line, re.IGNORECASE)
        if wtp_match:
            booking['wtp'] = float(wtp_match.group(1))
            
        # Extract channel
        channel_pattern = r'Channel:\s*(\w+)'
        channel_match = re.search(channel_pattern, line, re.IGNORECASE)
        if channel_match:
            booking['channel'] = channel_match.group(1)
            
        # Only add if we have meaningful data
        if 'origin' in booking and 'destination' in booking:
            self.bookings.append(booking)
            return booking
            
        return None
        
    def _parse_sale_notification(self, line, line_num):
        """Parse a sale notification (successful booking) from the log."""
        sale = {
            'line_number': line_num,
            'timestamp': self._extract_timestamp(line),
            'status': 'confirmed'
        }
        
        # Extract flight segments (e.g., "BA10/LHR-CDG/Y")
        segment_pattern = r'([A-Z0-9]{2,3}\d+)/([A-Z]{3})-([A-Z]{3})/([A-Z])'
        segments = re.findall(segment_pattern, line)
        
        if segments:
            sale['segments'] = []
            for seg in segments:
                sale['segments'].append({
                    'flight': seg[0],
                    'origin': seg[1],
                    'destination': seg[2],
                    'booking_class': seg[3]
                })
            
            # First segment origin and last segment destination
            if sale['segments']:
                sale['origin'] = sale['segments'][0]['origin']
                sale['destination'] = sale['segments'][-1]['destination']
                sale['flight_path'] = ' -> '.join([f"{s['flight']}" for s in sale['segments']])
                
        # Extract DTD (Days To Departure)
        dtd_pattern = r'[-+]?\d+\.\d+$'
        dtd_match = re.search(dtd_pattern, line.strip())
        if dtd_match:
            sale['days_to_departure'] = float(dtd_match.group(0))
            
        return sale if 'segments' in sale else None
        
    def _merge_sale_with_booking(self, sale_data):
        """Merge sale data with the most recent matching booking request."""
        # Find the most recent booking that matches this sale
        for booking in reversed(self.bookings):
            if (booking.get('status') == 'requested' and 
                booking.get('origin') == sale_data.get('origin') and
                booking.get('destination') == sale_data.get('destination')):
                
                # Merge sale data into booking
                booking.update(sale_data)
                booking['status'] = 'confirmed'
                self.statistics['successful_bookings'] += 1
                return
                
        # If no matching booking request found, add as standalone
        self.bookings.append(sale_data)
        self.statistics['successful_bookings'] += 1
        
    def _extract_timestamp(self, line):
        """Extract timestamp from log line."""
        # Common log timestamp patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            r'\[(\d{4}-\w{3}-\d{2}\s+\d{2}:\d{2}:\d{2})\]',
            r'(\d{2}:\d{2}:\d{2}\.\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        return None
        
    def calculate_statistics(self):
        """Calculate summary statistics from extracted bookings."""
        stats = {
            'total_bookings': len(self.bookings),
            'confirmed_bookings': sum(1 for b in self.bookings if b.get('status') == 'confirmed'),
            'requested_bookings': sum(1 for b in self.bookings if b.get('status') == 'requested'),
            'by_origin': defaultdict(int),
            'by_destination': defaultdict(int),
            'by_od_pair': defaultdict(int),
            'by_cabin': defaultdict(int),
            'by_channel': defaultdict(int),
            'party_size_dist': defaultdict(int),
            'avg_party_size': 0,
            'avg_wtp': 0,
            'avg_dtd': 0,
        }
        
        total_party_size = 0
        total_wtp = 0
        total_dtd = 0
        count_wtp = 0
        count_dtd = 0
        
        for booking in self.bookings:
            origin = booking.get('origin', 'Unknown')
            destination = booking.get('destination', 'Unknown')
            
            stats['by_origin'][origin] += 1
            stats['by_destination'][destination] += 1
            stats['by_od_pair'][f"{origin}-{destination}"] += 1
            
            if 'cabin' in booking:
                stats['by_cabin'][booking['cabin']] += 1
            if 'channel' in booking:
                stats['by_channel'][booking['channel']] += 1
            if 'party_size' in booking:
                party_size = booking['party_size']
                stats['party_size_dist'][party_size] += 1
                total_party_size += party_size
            if 'wtp' in booking:
                total_wtp += booking['wtp']
                count_wtp += 1
            if 'days_to_departure' in booking:
                total_dtd += booking['days_to_departure']
                count_dtd += 1
                
        if len(self.bookings) > 0:
            stats['avg_party_size'] = total_party_size / len(self.bookings)
        if count_wtp > 0:
            stats['avg_wtp'] = total_wtp / count_wtp
        if count_dtd > 0:
            stats['avg_dtd'] = total_dtd / count_dtd
            
        return stats
        
    def export_to_csv(self, output_file):
        """Export bookings to CSV format."""
        print(f"💾 Exporting to CSV: {output_file}")
        
        if not self.bookings:
            print("⚠️  No bookings to export!")
            return
            
        # Determine all unique fields
        all_fields = set()
        for booking in self.bookings:
            all_fields.update(booking.keys())
            
        # Define field order for better readability
        priority_fields = [
            'line_number', 'timestamp', 'status', 'origin', 'destination',
            'preferred_departure_date', 'request_date', 'party_size', 
            'cabin', 'channel', 'wtp', 'flight_path', 'days_to_departure'
        ]
        
        # Combine priority fields with remaining fields
        fieldnames = [f for f in priority_fields if f in all_fields]
        fieldnames.extend([f for f in sorted(all_fields) if f not in priority_fields])
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for booking in self.bookings:
                # Convert segments list to string if present
                if 'segments' in booking:
                    booking['segments_str'] = json.dumps(booking['segments'])
                writer.writerow(booking)
                
        print(f"✅ CSV export complete: {len(self.bookings)} records")
        
    def export_to_json(self, output_file):
        """Export bookings to JSON format."""
        print(f"💾 Exporting to JSON: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                'metadata': {
                    'source': self.log_file,
                    'extraction_date': datetime.now().isoformat(),
                    'total_bookings': len(self.bookings)
                },
                'bookings': self.bookings,
                'statistics': self.calculate_statistics()
            }, jsonfile, indent=2, default=str)
            
        print(f"✅ JSON export complete: {len(self.bookings)} records")
        
    def export_demand_forecast_format(self, output_file):
        """Export bookings in a format suitable for demand forecasting models."""
        print(f"💾 Exporting demand forecast format: {output_file}")
        
        # Aggregate bookings by date, route, and cabin
        demand_data = defaultdict(lambda: {
            'count': 0, 
            'total_passengers': 0,
            'avg_wtp': [],
            'avg_dtd': []
        })
        
        for booking in self.bookings:
            if booking.get('status') != 'confirmed':
                continue
                
            # Create key: date_origin_destination_cabin
            dep_date = booking.get('preferred_departure_date', 'Unknown')
            origin = booking.get('origin', 'Unknown')
            destination = booking.get('destination', 'Unknown')
            cabin = booking.get('cabin', 'Y')  # Default to Economy
            
            key = f"{dep_date}_{origin}_{destination}_{cabin}"
            
            demand_data[key]['count'] += 1
            demand_data[key]['date'] = dep_date
            demand_data[key]['origin'] = origin
            demand_data[key]['destination'] = destination
            demand_data[key]['cabin'] = cabin
            
            if 'party_size' in booking:
                demand_data[key]['total_passengers'] += booking['party_size']
            if 'wtp' in booking:
                demand_data[key]['avg_wtp'].append(booking['wtp'])
            if 'days_to_departure' in booking:
                demand_data[key]['avg_dtd'].append(booking['days_to_departure'])
                
        # Write aggregated data
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'departure_date', 'origin', 'destination', 'cabin',
                'booking_count', 'total_passengers', 'avg_wtp', 
                'avg_booking_lead_time', 'demand_level'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for key, data in sorted(demand_data.items()):
                avg_wtp = sum(data['avg_wtp']) / len(data['avg_wtp']) if data['avg_wtp'] else 0
                avg_dtd = sum(data['avg_dtd']) / len(data['avg_dtd']) if data['avg_dtd'] else 0
                
                # Categorize demand level
                if data['count'] >= 20:
                    demand_level = 'HIGH'
                elif data['count'] >= 10:
                    demand_level = 'MEDIUM'
                else:
                    demand_level = 'LOW'
                    
                writer.writerow({
                    'departure_date': data['date'],
                    'origin': data['origin'],
                    'destination': data['destination'],
                    'cabin': data['cabin'],
                    'booking_count': data['count'],
                    'total_passengers': data['total_passengers'],
                    'avg_wtp': f"{avg_wtp:.2f}",
                    'avg_booking_lead_time': f"{avg_dtd:.2f}",
                    'demand_level': demand_level
                })
                
        print(f"✅ Demand forecast export complete: {len(demand_data)} aggregated records")
        
    def print_statistics(self):
        """Print summary statistics to console."""
        stats = self.calculate_statistics()
        
        print("\n" + "="*60)
        print("📊 BOOKING STATISTICS SUMMARY")
        print("="*60)
        print(f"Total Bookings:       {stats['total_bookings']:,}")
        print(f"Confirmed Bookings:   {stats['confirmed_bookings']:,}")
        print(f"Requested Only:       {stats['requested_bookings']:,}")
        print(f"Avg Party Size:       {stats['avg_party_size']:.2f}")
        print(f"Avg WTP:              ${stats['avg_wtp']:.2f}")
        print(f"Avg Booking Lead:     {stats['avg_dtd']:.1f} days")
        
        print("\n📍 Top Origin Airports:")
        for origin, count in sorted(stats['by_origin'].items(), 
                                    key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {origin}: {count:,}")
            
        print("\n📍 Top Destination Airports:")
        for dest, count in sorted(stats['by_destination'].items(), 
                                  key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {dest}: {count:,}")
            
        print("\n✈️  Top O-D Pairs:")
        for od, count in sorted(stats['by_od_pair'].items(), 
                               key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {od}: {count:,}")
            
        if stats['by_cabin']:
            print("\n🎫 Cabin Distribution:")
            for cabin, count in sorted(stats['by_cabin'].items()):
                print(f"  {cabin}: {count:,}")
                
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Extract booking data from TvlSim simulation logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic CSV export
  python3 extract_bookings.py --log simulate.log --csv bookings.csv
  
  # Export to multiple formats
  python3 extract_bookings.py --log simulate.log --csv bookings.csv --json bookings.json
  
  # Export demand forecast format
  python3 extract_bookings.py --log simulate.log --demand demand_forecast.csv
  
  # Show statistics only
  python3 extract_bookings.py --log simulate.log --stats-only
        """
    )
    
    parser.add_argument('--log', '-l', 
                       default='simulate.log',
                       help='Input simulation log file (default: simulate.log)')
    parser.add_argument('--csv', '-c',
                       help='Output CSV file for raw bookings')
    parser.add_argument('--json', '-j',
                       help='Output JSON file for bookings with metadata')
    parser.add_argument('--demand', '-d',
                       help='Output CSV file in demand forecast format')
    parser.add_argument('--stats-only', '-s',
                       action='store_true',
                       help='Only display statistics, no export')
    
    args = parser.parse_args()
    
    # Create extractor and parse log
    extractor = BookingExtractor(args.log)
    extractor.parse_log()
    
    # Print statistics
    extractor.print_statistics()
    
    # Export to requested formats
    if not args.stats_only:
        if args.csv:
            extractor.export_to_csv(args.csv)
        if args.json:
            extractor.export_to_json(args.json)
        if args.demand:
            extractor.export_demand_forecast_format(args.demand)
            
        # If no output format specified, default to CSV
        if not (args.csv or args.json or args.demand):
            default_csv = 'bookings.csv'
            print(f"\n💡 No output format specified, using default: {default_csv}")
            extractor.export_to_csv(default_csv)


if __name__ == '__main__':
    main()
