#!/usr/bin/env python3
"""
PyIRI Year-long Plot Generator that Save to a Designated Output Directory
Created during the 2025 NASA Heliolab Ionosphere Team Project
Created by Frank Soboczenski, PhD 
Date: July, 31st, 2025 
Version: 1.01
Info: Generates plots similar to PyIRI_year_run.ipynb showing F10.7 input and NmF2 output
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

def generate_f107_data(year, daily=False):
    """Generate F10.7 data for a year with realistic variation"""
    if daily:
        # Generate daily values
        days = 365 if year % 4 != 0 else 366
        time = np.arange(days)
        
        # Create realistic F10.7 variation
        # Base level + annual variation + 27-day solar rotation + noise
        base = 110
        annual_var = 20 * np.sin(2 * np.pi * time / 365)
        rotation_var = 15 * np.sin(2 * np.pi * time / 27)
        noise = 10 * np.random.randn(days)
        
        f107 = base + annual_var + rotation_var + noise
        f107 = np.clip(f107, 70, 200)  # Keep within realistic bounds
        
        return time, f107
    else:
        # Monthly values
        months = np.arange(12)
        f107 = 110 + 20 * np.sin(2 * np.pi * months / 12) + 5 * np.random.randn(12)
        return months, f107

def main():
    parser = argparse.ArgumentParser(description='Generate year-long F10.7 and NmF2 plots')
    parser.add_argument('--year', type=int, default=2022, help='Year to process')
    parser.add_argument('--lat', type=float, default=40.0, help='Latitude')
    parser.add_argument('--lon', type=float, default=-100.0, help='Longitude')
    parser.add_argument('--hour', type=int, default=12, help='Hour UTC to extract')
    parser.add_argument('--output', type=str, default='/app/output', help='Output directory')
    parser.add_argument('--f107-constant', type=float, help='Use constant F10.7 instead of varying')
    parser.add_argument('--f107-file', type=str, help='Read F10.7 from file')
    
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
    
    # Initialize storage for results
    all_dates = []
    all_f107 = []
    all_nmf2 = []
    model_min = []
    model_max = []
    
    # Process each month
    for month in range(1, 13):
        print(f"\nProcessing {args.year}-{month:02d}...")
        
        # Get days in month
        if month == 12:
            next_month = datetime(args.year + 1, 1, 1)
        else:
            next_month = datetime(args.year, month + 1, 1)
        days_in_month = (next_month - datetime(args.year, month, 1)).days
        
        # Set up time array for the month
        ahr = np.array([args.hour])  # Single hour for speed
        
        # Get or generate F10.7 for this month
        if args.f107_constant:
            month_f107 = args.f107_constant
        else:
            # Generate varying F10.7
            month_f107 = 110 + 30 * np.sin(2 * np.pi * (month - 1) / 12) + 10 * np.random.randn()
            month_f107 = np.clip(month_f107, 70, 200)
        
        try:
            # Run PyIRI for this month - using monthly mean for speed
            f2, f1, e_peak, es_peak, sun, mag = ml.IRI_monthly_mean_par(
                args.year, month, ahr, alon, alat, PyIRI.coeff_dir, 0
            )
            
            # Extract NmF2 data
            # Handle different possible shapes
            nm_shape = f2['Nm'].shape
            print(f"  NmF2 shape: {nm_shape}")
            
            if len(nm_shape) == 3:
                # Shape is [time, location, solar] or similar
                nm_data = f2['Nm'][0, 0, 1] if nm_shape[2] > 1 else f2['Nm'][0, 0, 0]
                # Get min/max from solar indices
                nm_min_val = f2['Nm'][0, 0, 0]
                nm_max_val = f2['Nm'][0, 0, -1] if nm_shape[2] > 1 else nm_data * 1.3
            elif len(nm_shape) == 2:
                # Shape is [time, location] or [time, solar]
                if nm_shape[1] == 1:
                    nm_data = f2['Nm'][0, 0]
                else:
                    # Assume second dimension is solar activity
                    nm_data = f2['Nm'][0, 1] if nm_shape[1] > 1 else f2['Nm'][0, 0]
                    nm_min_val = f2['Nm'][0, 0]
                    nm_max_val = f2['Nm'][0, -1] if nm_shape[1] > 1 else nm_data * 1.3
            else:
                nm_data = f2['Nm'][0] if len(nm_shape) > 0 else f2['Nm']
                nm_min_val = nm_data * 0.7
                nm_max_val = nm_data * 1.3
            
            # For each day in month, store the data
            for day in range(1, days_in_month + 1):
                date = datetime(args.year, month, day, args.hour)
                all_dates.append(date)
                all_f107.append(month_f107)
                
                # Ensure we're appending scalar values
                if isinstance(nm_data, np.ndarray):
                    all_nmf2.append(float(nm_data.flatten()[0]))
                else:
                    all_nmf2.append(float(nm_data))
                
                # Model bounds
                if 'nm_min_val' in locals() and 'nm_max_val' in locals():
                    if isinstance(nm_min_val, np.ndarray):
                        model_min.append(float(nm_min_val.flatten()[0]))
                        model_max.append(float(nm_max_val.flatten()[0]))
                    else:
                        model_min.append(float(nm_min_val))
                        model_max.append(float(nm_max_val))
                else:
                    # Use default bounds
                    val = all_nmf2[-1]
                    model_min.append(val * 0.7)
                    model_max.append(val * 1.3)
                
        except Exception as e:
            print(f"  Error processing month {month}: {e}")
            # Fill with NaN for failed months
            for day in range(1, days_in_month + 1):
                date = datetime(args.year, month, day, args.hour)
                all_dates.append(date)
                all_f107.append(month_f107)
                all_nmf2.append(np.nan)
                model_min.append(np.nan)
                model_max.append(np.nan)
    
    # Convert to arrays and ensure they're 1D
    all_dates = np.array(all_dates)
    all_f107 = np.array(all_f107).flatten()
    all_nmf2 = np.array(all_nmf2).flatten()
    model_min = np.array(model_min).flatten()
    model_max = np.array(model_max).flatten()
    
    # Verify shapes
    print(f"\nData shapes - dates: {all_dates.shape}, f107: {all_f107.shape}, "
          f"nmf2: {all_nmf2.shape}, min: {model_min.shape}, max: {model_max.shape}")
    
    # Create the plot similar to the notebook
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot 1: F10.7
    ax1.plot(all_dates, model_min[0] * np.ones_like(all_dates), 'b-', label='Model Min', linewidth=1)
    ax1.plot(all_dates, model_max[0] * np.ones_like(all_dates), 'r-', label='Model Max', linewidth=1)
    ax1.plot(all_dates, all_f107, 'g-', label='User Input', linewidth=2)
    ax1.set_ylabel('F10.7', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(50, 250)
    
    # Plot 2: NmF2 with uncertainty bands
    # Fill between model bounds
    ax2.fill_between(all_dates, model_min, model_max, 
                     where=(model_max >= model_min), 
                     interpolate=True, alpha=0.5, 
                     facecolor='blue', label='Model Min')
    ax2.fill_between(all_dates, model_max, all_nmf2, 
                     where=(all_nmf2 >= model_max), 
                     interpolate=True, alpha=0.5, 
                     facecolor='red', label='Model Max')
    ax2.fill_between(all_dates, model_min, all_nmf2, 
                     where=(all_nmf2 >= model_min) & (all_nmf2 <= model_max), 
                     interpolate=True, alpha=0.5, 
                     facecolor='green', label='Output')
    
    ax2.set_ylabel('NmF2', fontsize=12)
    ax2.set_xlabel('Time', fontsize=12)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # Format x-axis
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=0)
    
    # Add title
    fig.suptitle(f'PyIRI Year Run - {location_name} - {args.year} at {args.hour:02d}:00 UTC', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    output_path = os.path.join(args.output, f'year_plot_{location_name}_{args.year}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"\n✓ Year plot saved: {output_path} ({size} bytes)")
    else:
        print(f"\n✗ Year plot failed to save")
    
    # Also save the data as CSV
    csv_path = os.path.join(args.output, f'year_data_{location_name}_{args.year}.csv')
    with open(csv_path, 'w') as f:
        f.write("Date,F107,NmF2,Model_Min,Model_Max\n")
        for i in range(len(all_dates)):
            f.write(f"{all_dates[i].strftime('%Y-%m-%d')},{all_f107[i]:.1f},"
                   f"{all_nmf2[i]:.2e},{model_min[i]:.2e},{model_max[i]:.2e}\n")
    print(f"✓ Data saved: {csv_path}")

if __name__ == "__main__":
    main()