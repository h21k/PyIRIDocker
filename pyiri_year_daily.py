#!/usr/bin/env python3
"""
PyIRI Year-long Plot Generator - Daily Resolutio that Save to a Designated Output Directory
Created during the 2025 NASA Heliolab Ionosphere Team Project
Created by Frank Soboczenski, PhD 
Date: July, 31st, 2025 
Version: 1.01
Info: Generates plots with daily resolution similar to PyIRI_year_run.ipynb
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import sys

# Import PyIRI modules
import PyIRI
import PyIRI.edp_update as ml

def generate_f107_timeseries(year):
    """Generate realistic F10.7 time series for a year"""
    # Create date range
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    days = (end_date - start_date).days + 1
    
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Generate F10.7 with multiple components
    t = np.arange(days)
    
    # Base solar cycle trend
    base = 110
    
    # Annual variation
    annual = 20 * np.sin(2 * np.pi * t / 365.25)
    
    # 27-day solar rotation
    rotation = 15 * np.sin(2 * np.pi * t / 27)
    
    # Occasional flares
    flares = np.zeros(days)
    n_flares = int(days / 30)  # About one per month
    flare_days = np.random.choice(days, n_flares, replace=False)
    for fd in flare_days:
        # Flare lasts 2-5 days
        duration = np.random.randint(2, 6)
        amplitude = np.random.uniform(30, 80)
        for i in range(duration):
            if fd + i < days:
                flares[fd + i] += amplitude * np.exp(-i/2)
    
    # Random daily variation
    daily_var = 5 * np.random.randn(days)
    
    # Combine all components
    f107 = base + annual + rotation + flares + daily_var
    
    # Apply realistic bounds
    f107 = np.clip(f107, 70, 250)
    
    return dates, f107

def main():
    parser = argparse.ArgumentParser(description='Generate year-long F10.7 and NmF2 plots with daily resolution')
    parser.add_argument('--year', type=int, default=2022, help='Year to process')
    parser.add_argument('--lat', type=float, default=40.0, help='Latitude')
    parser.add_argument('--lon', type=float, default=-100.0, help='Longitude')
    parser.add_argument('--hour', type=int, default=12, help='Hour UTC to extract')
    parser.add_argument('--output', type=str, default='/app/output', help='Output directory')
    parser.add_argument('--use-edp', action='store_true', help='Use daily EDP calculation (slower)')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    print(f"Output directory: {args.output}")
    
    # Set up location
    alon = np.array([args.lon])
    alat = np.array([args.lat])
    location_name = f"{args.lat}N_{args.lon}E"
    
    print(f"Processing year {args.year} for location {location_name}")
    print(f"Extracting data for {args.hour:02d}:00 UTC")
    
    # Generate F10.7 time series
    print("Generating F10.7 time series...")
    dates, f107_values = generate_f107_timeseries(args.year)
    
    # Initialize storage
    nmf2_values = []
    nmf2_min = []
    nmf2_max = []
    
    # Process in chunks (monthly) for efficiency
    print("\nProcessing ionospheric parameters...")
    
    for month in range(1, 13):
        print(f"  Month {month:02d}/{12}...", end='', flush=True)
        
        # Get days in this month
        month_start = datetime(args.year, month, 1)
        if month == 12:
            month_end = datetime(args.year + 1, 1, 1)
        else:
            month_end = datetime(args.year, month + 1, 1)
        
        month_days = []
        month_f107 = []
        for i, date in enumerate(dates):
            if month_start <= date < month_end:
                month_days.append(i)
                month_f107.append(f107_values[i])
        
        if not month_days:
            continue
            
        # Average F10.7 for the month
        avg_f107 = np.mean(month_f107)
        
        try:
            # Run PyIRI for this month
            ahr = np.array([args.hour])
            
            if args.use_edp:
                # Daily calculation with EDP (slower but more accurate)
                # Process each day
                for day_idx, day_f107 in zip(month_days, month_f107):
                    date = dates[day_idx]
                    aalt = np.arange(60, 1000, 50)  # Coarse altitude grid for speed
                    
                    f2, f1, e_peak, es_peak, sun, mag, edp = ml.IRI_density_1day(
                        date.year, date.month, date.day, ahr, alon, alat, 
                        aalt, day_f107, PyIRI.coeff_dir, 0
                    )
                    
                    # Extract NmF2
                    if len(f2['Nm'].shape) >= 2:
                        nm = f2['Nm'][0, 0]
                    else:
                        nm = f2['Nm'][0] if len(f2['Nm'].shape) > 0 else f2['Nm']
                    
                    nmf2_values.append(nm)
                    nmf2_min.append(nm * 0.8)  # Approximate bounds
                    nmf2_max.append(nm * 1.2)
            else:
                # Monthly mean calculation (faster)
                f2, f1, e_peak, es_peak, sun, mag = ml.IRI_monthly_mean_par(
                    args.year, month, ahr, alon, alat, PyIRI.coeff_dir, 0
                )
                
                # Extract NmF2 for different solar conditions
                if len(f2['Nm'].shape) == 3:
                    # [time, location, solar]
                    nm_avg = f2['Nm'][0, 0, 1]  # Middle solar activity
                    nm_min = f2['Nm'][0, 0, 0]  # Solar minimum
                    nm_max = f2['Nm'][0, 0, -1] # Solar maximum
                elif len(f2['Nm'].shape) == 2:
                    nm_avg = f2['Nm'][0, 0]
                    nm_min = nm_avg * 0.7
                    nm_max = nm_avg * 1.3
                else:
                    nm_avg = f2['Nm'][0] if len(f2['Nm'].shape) > 0 else f2['Nm']
                    nm_min = nm_avg * 0.7
                    nm_max = nm_avg * 1.3
                
                # Apply to all days in month with daily F10.7 scaling
                for day_idx, day_f107 in zip(month_days, month_f107):
                    # Scale based on F10.7 deviation from average
                    scale = (day_f107 - 70) / (avg_f107 - 70) if avg_f107 > 70 else 1.0
                    scale = np.clip(scale, 0.5, 2.0)
                    
                    nmf2_values.append(nm_avg * scale)
                    nmf2_min.append(nm_min)
                    nmf2_max.append(nm_max)
            
            print(" ✓")
            
        except Exception as e:
            print(f" ✗ Error: {e}")
            # Fill with NaN
            for _ in month_days:
                nmf2_values.append(np.nan)
                nmf2_min.append(np.nan)
                nmf2_max.append(np.nan)
    
    # Convert to arrays
    dates = np.array(dates)
    f107_values = np.array(f107_values)
    nmf2_values = np.array(nmf2_values)
    nmf2_min = np.array(nmf2_min)
    nmf2_max = np.array(nmf2_max)
    
    # Create the plot
    print("\nCreating plot...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, 
                                   gridspec_kw={'height_ratios': [1, 1]})
    
    # Plot 1: F10.7
    ax1.axhline(y=70, color='blue', linestyle='-', linewidth=1, label='Model Min')
    ax1.axhline(y=180, color='red', linestyle='-', linewidth=1, label='Model Max')
    ax1.plot(dates, f107_values, 'g-', linewidth=1.5, label='User Input')
    ax1.set_ylabel('F10.7', fontsize=12)
    ax1.legend(loc='upper right', framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(50, 250)
    
    # Plot 2: NmF2 with colored bands
    # Create filled regions similar to the notebook
    for i in range(len(dates)-1):
        if not np.isnan(nmf2_values[i]):
            # Determine color based on value relative to bounds
            if nmf2_values[i] < nmf2_min[i]:
                color = 'blue'
                bottom = nmf2_values[i]
                top = nmf2_min[i]
            elif nmf2_values[i] > nmf2_max[i]:
                color = 'red'
                bottom = nmf2_max[i]
                top = nmf2_values[i]
            else:
                color = 'green'
                bottom = nmf2_min[i]
                top = nmf2_max[i]
            
            # Fill the region
            ax2.fill_between([dates[i], dates[i+1]], 
                           [bottom, bottom], [top, top],
                           color=color, alpha=0.6, edgecolor='none')
    
    # Add the actual line...I know... I know...
    ax2.plot(dates, nmf2_values, 'k-', linewidth=0.5, alpha=0.8)
    
    # Create custom legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='blue', alpha=0.6, label='Model Min'),
        Patch(facecolor='red', alpha=0.6, label='Model Max'),
        Patch(facecolor='green', alpha=0.6, label='Output')
    ]
    ax2.legend(handles=legend_elements, loc='upper right', framealpha=0.9)
    
    ax2.set_ylabel('NmF2', fontsize=12)
    ax2.set_xlabel('Time', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(bottom=0)
    
    # Format x-axis
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    fig.autofmt_xdate(rotation=45)
    
    # Add title
    title = f'PyIRI Year Run - {location_name} - {args.year} at {args.hour:02d}:00 UTC'
    if args.use_edp:
        title += ' (Daily EDP)'
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    suffix = '_daily' if args.use_edp else ''
    output_path = os.path.join(args.output, f'year_plot_{location_name}_{args.year}{suffix}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"\n✓ Year plot saved: {output_path} ({size:,} bytes)")
    else:
        print(f"\n✗ Year plot failed to save")
    
    # Save data as CSV
    csv_path = os.path.join(args.output, f'year_data_{location_name}_{args.year}{suffix}.csv')
    with open(csv_path, 'w') as f:
        f.write("Date,F107,NmF2,NmF2_Min,NmF2_Max\n")
        for i in range(len(dates)):
            f.write(f"{dates[i].strftime('%Y-%m-%d')},{f107_values[i]:.1f},"
                   f"{nmf2_values[i]:.3e},{nmf2_min[i]:.3e},{nmf2_max[i]:.3e}\n")
    print(f"✓ Data saved: {csv_path}")
    
    # Print summary statistics
    print(f"\nSummary Statistics:")
    print(f"  F10.7: min={np.nanmin(f107_values):.1f}, "
          f"max={np.nanmax(f107_values):.1f}, "
          f"mean={np.nanmean(f107_values):.1f}")
    print(f"  NmF2:  min={np.nanmin(nmf2_values):.2e}, "
          f"max={np.nanmax(nmf2_values):.2e}, "
          f"mean={np.nanmean(nmf2_values):.2e}")

if __name__ == "__main__":
    main()