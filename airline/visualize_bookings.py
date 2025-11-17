#!/usr/bin/env python3
"""
Simple Booking Data Visualizer for TvlSim
Generates charts and visualizations from extracted booking data
"""

import pandas as pd
import sys
import os

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("⚠️  matplotlib/seaborn not installed. Install with:")
    print("   pip3 install matplotlib seaborn")
    print("\nWill generate text-based summaries instead.\n")


def plot_demand_forecast(csv_file, output_dir='plots'):
    """Generate visualizations from demand forecast data."""
    
    # Read data
    print(f"📊 Loading data from: {csv_file}")
    df = pd.read_csv(csv_file)
    
    if df.empty:
        print("❌ No data found in file!")
        return
    
    print(f"✅ Loaded {len(df)} records\n")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    if HAS_PLOTTING:
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        
        # 1. Top routes bar chart
        print("📈 Generating route demand chart...")
        df['route'] = df['origin'] + '-' + df['destination']
        top_routes = df.groupby('route')['booking_count'].sum().sort_values(ascending=False).head(15)
        
        plt.figure(figsize=(12, 6))
        top_routes.plot(kind='barh', color='steelblue')
        plt.title('Top 15 Routes by Booking Volume', fontsize=16, fontweight='bold')
        plt.xlabel('Number of Bookings')
        plt.ylabel('Route')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/top_routes.png', dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved: {output_dir}/top_routes.png")
        plt.close()
        
        # 2. Demand level distribution
        print("📈 Generating demand level distribution...")
        plt.figure(figsize=(8, 6))
        demand_counts = df['demand_level'].value_counts()
        colors = {'HIGH': '#ff4444', 'MEDIUM': '#ffaa00', 'LOW': '#44ff44'}
        demand_counts.plot(kind='pie', autopct='%1.1f%%', 
                          colors=[colors.get(x, 'gray') for x in demand_counts.index])
        plt.title('Demand Level Distribution', fontsize=16, fontweight='bold')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/demand_distribution.png', dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved: {output_dir}/demand_distribution.png")
        plt.close()
        
        # 3. Booking lead time distribution
        if 'avg_booking_lead_time' in df.columns:
            print("📈 Generating booking lead time distribution...")
            plt.figure(figsize=(10, 6))
            df['avg_booking_lead_time'].hist(bins=30, color='coral', edgecolor='black')
            plt.title('Booking Lead Time Distribution', fontsize=16, fontweight='bold')
            plt.xlabel('Days Before Departure')
            plt.ylabel('Frequency')
            plt.axvline(df['avg_booking_lead_time'].median(), color='red', 
                       linestyle='--', linewidth=2, label=f'Median: {df["avg_booking_lead_time"].median():.1f} days')
            plt.legend()
            plt.tight_layout()
            plt.savefig(f'{output_dir}/lead_time_distribution.png', dpi=300, bbox_inches='tight')
            print(f"   ✅ Saved: {output_dir}/lead_time_distribution.png")
            plt.close()
        
        # 4. Cabin class distribution
        print("📈 Generating cabin class distribution...")
        plt.figure(figsize=(10, 6))
        cabin_bookings = df.groupby('cabin')['booking_count'].sum().sort_values(ascending=False)
        cabin_bookings.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Bookings by Cabin Class', fontsize=16, fontweight='bold')
        plt.xlabel('Cabin Class')
        plt.ylabel('Number of Bookings')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/cabin_distribution.png', dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved: {output_dir}/cabin_distribution.png")
        plt.close()
        
        # 5. WTP vs Lead Time scatter
        if 'avg_wtp' in df.columns and 'avg_booking_lead_time' in df.columns:
            print("📈 Generating WTP vs Lead Time scatter...")
            plt.figure(figsize=(10, 6))
            scatter = plt.scatter(df['avg_booking_lead_time'], df['avg_wtp'], 
                                c=df['booking_count'], cmap='viridis', 
                                s=100, alpha=0.6, edgecolors='black')
            plt.colorbar(scatter, label='Booking Count')
            plt.title('Willingness to Pay vs Booking Lead Time', fontsize=16, fontweight='bold')
            plt.xlabel('Days Before Departure')
            plt.ylabel('Average WTP ($)')
            plt.tight_layout()
            plt.savefig(f'{output_dir}/wtp_vs_leadtime.png', dpi=300, bbox_inches='tight')
            print(f"   ✅ Saved: {output_dir}/wtp_vs_leadtime.png")
            plt.close()
        
        print(f"\n✨ All visualizations saved to: {output_dir}/")
    
    # Text-based summary (always generate)
    print("\n" + "="*70)
    print("📊 DEMAND FORECAST SUMMARY")
    print("="*70)
    
    print(f"\nTotal Records: {len(df):,}")
    print(f"Total Bookings: {df['booking_count'].sum():,}")
    print(f"Total Passengers: {df['total_passengers'].sum():,}")
    
    print("\n📍 Top 10 Routes:")
    df['route'] = df['origin'] + '-' + df['destination']
    top_routes = df.groupby('route')['booking_count'].sum().sort_values(ascending=False).head(10)
    for i, (route, count) in enumerate(top_routes.items(), 1):
        print(f"   {i:2d}. {route:12s} : {count:5,} bookings")
    
    print("\n🎫 Demand Levels:")
    for level in ['HIGH', 'MEDIUM', 'LOW']:
        count = (df['demand_level'] == level).sum()
        pct = count / len(df) * 100
        print(f"   {level:8s}: {count:5,} records ({pct:5.1f}%)")
    
    print("\n💰 Financial Summary:")
    if 'avg_wtp' in df.columns:
        print(f"   Average WTP: ${df['avg_wtp'].mean():,.2f}")
        print(f"   Max WTP: ${df['avg_wtp'].max():,.2f}")
        print(f"   Min WTP: ${df['avg_wtp'].min():,.2f}")
    
    print("\n⏱  Booking Behavior:")
    if 'avg_booking_lead_time' in df.columns:
        print(f"   Avg Lead Time: {df['avg_booking_lead_time'].mean():.1f} days")
        print(f"   Median Lead Time: {df['avg_booking_lead_time'].median():.1f} days")
        print(f"   Max Lead Time: {df['avg_booking_lead_time'].max():.1f} days")
    
    print("="*70 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 visualize_bookings.py <demand_forecast.csv>")
        print("\nExample:")
        print("  python3 visualize_bookings.py booking_data_*/demand_forecast.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: File '{csv_file}' not found!")
        sys.exit(1)
    
    plot_demand_forecast(csv_file)


if __name__ == '__main__':
    main()
