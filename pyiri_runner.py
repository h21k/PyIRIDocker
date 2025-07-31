#!/usr/bin/env python3
"""
PyIRI Simple Runner Script with Plots that Save to a Designated Output Directory
Created during the 2025 NASA Heliolab Ionosphere Team Project
Created by Frank Soboczenski, PhD 
Date: July, 31st, 2025 
Version: 1.01
Info: Version that handles the actual PyIRI data structure
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Import PyIRI modules
import PyIRI
import PyIRI.edp_update as ml
import PyIRI.plotting as plot

def main():
    parser = argparse.ArgumentParser(description='Simple PyIRI with guaranteed plot output')
    parser.add_argument('--global-map', action='store_true', help='Generate global map')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lon', type=float, help='Longitude')
    parser.add_argument('--resolution', type=float, default=5.0, help='Grid resolution')
    parser.add_argument('--year', type=int, default=2020, help='Year')
    parser.add_argument('--month', type=int, default=4, help='Month')
    parser.add_argument('--day', type=int, default=15, help='Day')
    parser.add_argument('--hour', type=int, default=12, help='Hour')
    parser.add_argument('--f107', type=float, default=100, help='F10.7 solar flux')
    parser.add_argument('--output', type=str, default='/app/output', help='Output directory')
    parser.add_argument('--parameters', nargs='+', default=['foF2'], help='Parameters to plot')
    parser.add_argument('--daily', action='store_true', help='Use daily parameters with EDP (from Daily_parameters.ipynb)')
    parser.add_argument('--profiles', action='store_true', help='Create electron density profiles')
    parser.add_argument('--vtec', action='store_true', help='Calculate and plot vTEC')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    print(f"Output directory: {args.output}")
    
    # Create grid
    if args.global_map:
        print("Creating global grid...")
        dlon = dlat = args.resolution
        lons = np.arange(-180, 180, dlon)
        lats = np.arange(-90, 90 + dlat, dlat)
        alon_2d, alat_2d = np.meshgrid(lons, lats)
        alon = alon_2d.flatten()
        alat = alat_2d.flatten()
        location_name = f"Global_{args.resolution}deg"
    else:
        alon = np.array([args.lon])
        alat = np.array([args.lat])
        alon_2d = alat_2d = None
        location_name = f"{args.lat}N_{args.lon}E"
    
    print(f"Grid size: {len(alon)} points")
    
    # Calculate parameters
    ahr = np.arange(0, 24, 1)
    print("Running PyIRI calculation...")
    
    try:
        if args.daily or args.profiles or args.vtec:
            # Daily parameters with electron density profiles (Daily_parameters.ipynb)
            print("Using daily parameters with electron density profiles...")
            aalt = np.arange(60, 1000 + 10, 10)  # Altitude array for EDP
            f2, f1, e_peak, es_peak, sun, mag, edp = ml.IRI_density_1day(
                args.year, args.month, args.day, ahr, alon, alat, aalt, args.f107, PyIRI.coeff_dir, 0
            )
            has_edp = True
        else:
            # Monthly mean parameters (faster, no EDP)
            f2, f1, e_peak, es_peak, sun, mag = ml.IRI_monthly_mean_par(
                args.year, args.month, ahr, alon, alat, PyIRI.coeff_dir, 0
            )
            edp = None
            aalt = None
            has_edp = False
            
        print("✓ PyIRI calculation complete")
        
        # Debug: Print shapes and structure
        print(f"\nDebug - Data shapes:")
        print(f"  f2['fo'] shape: {f2['fo'].shape}")
        print(f"  f2 keys: {list(f2.keys())}")
        if has_edp and edp is not None:
            print(f"  edp shape: {edp.shape}")
            
    except Exception as e:
        print(f"✗ PyIRI calculation failed: {e}")
        return
    
    # Create simple plots that WILL work
    timestamp = f"{args.year}{args.month:02d}{args.day:02d}_{args.hour:02d}UTC"
    
    if args.global_map and alon_2d is not None:
        # Global plots
        print("\nCreating global plots...")
        
        # Extract data - handle different possible shapes
        # PyIRI typically returns [time, location] for global grids
        try:
            # Check the actual shape and extract accordingly
            if len(f2['fo'].shape) == 2:
                # Shape is [time, location]
                fo_data = f2['fo'][args.hour, :]  # Extract data for specific hour
                hm_data = f2['hm'][args.hour, :]
                nm_data = f2['Nm'][args.hour, :]
            elif len(f2['fo'].shape) == 3:
                # Shape might be [time, location, solar]
                fo_data = f2['fo'][args.hour, :, -1]  # Use last index (might be solar max)
                hm_data = f2['hm'][args.hour, :, -1]
                nm_data = f2['Nm'][args.hour, :, -1]
            else:
                print(f"Unexpected f2['fo'] shape: {f2['fo'].shape}")
                return
                
            # Reshape to 2D grid
            fo_2d = fo_data.reshape(alon_2d.shape)
            hm_2d = hm_data.reshape(alon_2d.shape)
            nm_2d = nm_data.reshape(alon_2d.shape)
            
        except Exception as e:
            print(f"Error extracting data: {e}")
            print(f"f2['fo'] shape: {f2['fo'].shape}")
            return
        
        # Plot foF2
        if 'foF2' in args.parameters or 'all' in args.parameters:
            plt.figure(figsize=(12, 8))
            cs = plt.contourf(alon_2d, alat_2d, fo_2d, levels=20, cmap='plasma')
            plt.colorbar(cs, label='foF2 (MHz)')
            plt.xlabel('Longitude (°)')
            plt.ylabel('Latitude (°)')
            plt.title(f'F2 Critical Frequency - {timestamp}')
            plt.grid(True, alpha=0.3)
            
            output_path = os.path.join(args.output, f'foF2_{location_name}_{timestamp}.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"✓ foF2 plot saved: {output_path} ({size} bytes)")
            else:
                print(f"✗ foF2 plot failed to save")
        
        # Plot hmF2
        if 'hmF2' in args.parameters or 'all' in args.parameters:
            plt.figure(figsize=(12, 8))
            cs = plt.contourf(alon_2d, alat_2d, hm_2d, levels=20, cmap='viridis')
            plt.colorbar(cs, label='hmF2 (km)')
            plt.xlabel('Longitude (°)')
            plt.ylabel('Latitude (°)')
            plt.title(f'F2 Peak Height - {timestamp}')
            plt.grid(True, alpha=0.3)
            
            output_path = os.path.join(args.output, f'hmF2_{location_name}_{timestamp}.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"✓ hmF2 plot saved: {output_path} ({size} bytes)")
            else:
                print(f"✗ hmF2 plot failed to save")
        
        # Plot NmF2
        if 'NmF2' in args.parameters or 'all' in args.parameters:
            plt.figure(figsize=(12, 8))
            cs = plt.contourf(alon_2d, alat_2d, nm_2d, levels=20, cmap='inferno')
            plt.colorbar(cs, label='NmF2 (el/cm³)')
            plt.xlabel('Longitude (°)')
            plt.ylabel('Latitude (°)')
            plt.title(f'F2 Peak Density - {timestamp}')
            plt.grid(True, alpha=0.3)
            
            output_path = os.path.join(args.output, f'NmF2_{location_name}_{timestamp}.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"✓ NmF2 plot saved: {output_path} ({size} bytes)")
            else:
                print(f"✗ NmF2 plot failed to save")
        
        # Plot vTEC if requested and EDP available
        if args.vtec and has_edp and edp is not None:
            print("Calculating vTEC...")
            try:
                # Manual vTEC calculation (integrate electron density over altitude)
                alt_step = aalt[1] - aalt[0]  # km
                
                # Handle different possible EDP shapes
                print(f"  EDP shape for vTEC: {edp.shape}")
                
                if len(edp.shape) == 3:
                    # Determine which axis is altitude by checking sizes
                    if edp.shape[1] == len(aalt):  # Shape is [time, altitude, location]
                        print("  Integrating over altitude axis 1")
                        # Use trapezoid instead of deprecated trapz
                        if hasattr(np, 'trapezoid'):
                            tec_values = np.trapezoid(edp, axis=1, dx=alt_step * 1000)  # Integrate over altitude
                        else:
                            tec_values = np.trapz(edp, axis=1, dx=alt_step * 1000)  # Fallback for older numpy
                        tec_data = tec_values[args.hour, :]  # Extract [location] for specific hour
                    elif edp.shape[2] == len(aalt):  # Shape is [time, location, altitude]
                        print("  Integrating over altitude axis 2")
                        if hasattr(np, 'trapezoid'):
                            tec_values = np.trapezoid(edp, axis=2, dx=alt_step * 1000)  # Integrate over altitude
                        else:
                            tec_values = np.trapz(edp, axis=2, dx=alt_step * 1000)  # Fallback
                        tec_data = tec_values[args.hour, :]  # Extract [location] for specific hour
                    else:
                        print(f"  Cannot determine altitude axis. aalt length: {len(aalt)}")
                        raise ValueError("Cannot determine altitude axis")
                elif len(edp.shape) == 2:
                    # Shape might be [location, altitude] for single time
                    if edp.shape[1] == len(aalt):
                        if hasattr(np, 'trapezoid'):
                            tec_values = np.trapezoid(edp, axis=1, dx=alt_step * 1000)
                        else:
                            tec_values = np.trapz(edp, axis=1, dx=alt_step * 1000)
                        tec_data = tec_values
                    else:
                        if hasattr(np, 'trapezoid'):
                            tec_values = np.trapezoid(edp, axis=0, dx=alt_step * 1000)
                        else:
                            tec_values = np.trapz(edp, axis=0, dx=alt_step * 1000)
                        tec_data = tec_values
                else:
                    print(f"Unexpected EDP shape: {edp.shape}")
                    raise ValueError("Cannot process EDP data")
                
                # Convert to TECU (1 TECU = 10^16 electrons/m^2)
                tec_data = tec_data * 1e-16
                
                print(f"  TEC data shape: {tec_data.shape}")
                print(f"  Grid shape: {alon_2d.shape}")
                
                # Ensure tec_data can be reshaped to grid
                if tec_data.size != alon_2d.size:
                    print(f"  Warning: TEC data size ({tec_data.size}) doesn't match grid size ({alon_2d.size})")
                    # Try to extract the correct portion
                    if tec_data.size > alon_2d.size:
                        tec_data = tec_data[:alon_2d.size]
                    else:
                        raise ValueError(f"TEC data too small: {tec_data.size} < {alon_2d.size}")
                
                tec_2d = tec_data.reshape(alon_2d.shape)
                
                plt.figure(figsize=(12, 8))
                cs = plt.contourf(alon_2d, alat_2d, tec_2d, levels=20, cmap='turbo')
                plt.colorbar(cs, label='vTEC (TECU)')
                plt.xlabel('Longitude (°)')
                plt.ylabel('Latitude (°)')
                plt.title(f'Vertical Total Electron Content - {timestamp}')
                plt.grid(True, alpha=0.3)
                
                output_path = os.path.join(args.output, f'vTEC_{location_name}_{timestamp}.png')
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                if os.path.exists(output_path):
                    size = os.path.getsize(output_path)
                    print(f"✓ vTEC plot saved: {output_path} ({size} bytes)")
                else:
                    print(f"✗ vTEC plot failed to save")
                    
            except Exception as e:
                print(f"✗ vTEC calculation failed: {e}")
    
    else:
        # Single location plots
        print("\nCreating time series plots...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Extract time series - handle different shapes
        if len(f2['fo'].shape) == 2:
            # Shape is [time, location]
            fo_time = f2['fo'][:, 0]  # First location
            hm_time = f2['hm'][:, 0]
            nm_time = f2['Nm'][:, 0]
            e_nm_time = e_peak['Nm'][:, 0]
        elif len(f2['fo'].shape) == 3:
            # Shape is [time, location, solar]
            fo_time = f2['fo'][:, 0, -1]  # First location, last solar index
            hm_time = f2['hm'][:, 0, -1]
            nm_time = f2['Nm'][:, 0, -1]
            e_nm_time = e_peak['Nm'][:, 0, -1]
        else:
            # Shape is just [time]
            fo_time = f2['fo'][:]
            hm_time = f2['hm'][:]
            nm_time = f2['Nm'][:]
            e_nm_time = e_peak['Nm'][:]
        
        ax1.plot(ahr, fo_time, 'b-', linewidth=2)
        ax1.set_xlabel('Hour (UTC)')
        ax1.set_ylabel('foF2 (MHz)')
        ax1.grid(True, alpha=0.3)
        ax1.set_title('F2 Critical Frequency')
        
        ax2.plot(ahr, hm_time, 'r-', linewidth=2)
        ax2.set_xlabel('Hour (UTC)')
        ax2.set_ylabel('hmF2 (km)')
        ax2.grid(True, alpha=0.3)
        ax2.set_title('F2 Peak Height')
        
        ax3.plot(ahr, nm_time, 'g-', linewidth=2)
        ax3.set_xlabel('Hour (UTC)')
        ax3.set_ylabel('NmF2 (el/cm³)')
        ax3.set_yscale('log')
        ax3.grid(True, alpha=0.3)
        ax3.set_title('F2 Peak Density')
        
        ax4.plot(ahr, e_nm_time, 'm-', linewidth=2)
        ax4.set_xlabel('Hour (UTC)')
        ax4.set_ylabel('NmE (el/cm³)')
        ax4.set_yscale('log')
        ax4.grid(True, alpha=0.3)
        ax4.set_title('E Layer Peak Density')
        
        plt.suptitle(f'Ionospheric Parameters - {location_name} - {timestamp}', fontsize=16)
        plt.tight_layout()
        
        output_path = os.path.join(args.output, f'timeseries_{location_name}_{timestamp}.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"✓ Time series plot saved: {output_path} ({size} bytes)")
        else:
            print(f"✗ Time series plot failed to save")
    
    # Create electron density profiles if requested
    if args.profiles and has_edp and edp is not None:
        print("\nCreating electron density profiles...")
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
            
            # Plot 1: Density profile at specific hour
            if len(edp.shape) == 3:  # Could be [time, altitude, location] or [time, location, altitude]
                # Determine the order by checking dimensions
                if edp.shape[1] == len(aalt):  # [time, altitude, location]
                    density_profile = edp[args.hour, :, 0].flatten()  # Extract and flatten
                    edp_cross = edp[:, :, 0].T  # [altitude, time] for contour
                elif edp.shape[2] == len(aalt):  # [time, location, altitude]
                    density_profile = edp[args.hour, 0, :].flatten()
                    edp_cross = edp[:, 0, :].T  # [altitude, time] for contour
                else:
                    print(f"Cannot determine altitude axis in shape {edp.shape}")
                    density_profile = None
                    edp_cross = None
            elif len(edp.shape) == 2:  # [location, altitude] or [time, altitude]
                if edp.shape[0] == len(ahr):  # [time, altitude]
                    density_profile = edp[args.hour, :].flatten()
                    edp_cross = edp.T
                else:  # [location, altitude]
                    density_profile = edp[0, :].flatten()  # First location
                    edp_cross = None
            else:
                density_profile = edp[:].flatten()
                edp_cross = None
            
            if density_profile is not None:
                # Ensure density_profile and aalt have compatible shapes
                print(f"  Density profile shape: {density_profile.shape}, aalt shape: {aalt.shape}")
                
                ax1.plot(density_profile, aalt, 'b-', linewidth=2)
                ax1.set_xlabel('Electron Density (el/cm³)')
                ax1.set_ylabel('Altitude (km)')
                ax1.set_xscale('log')
                ax1.grid(True, alpha=0.3)
                ax1.set_title(f'Electron Density Profile\n{location_name} at {args.hour:02d}:00 UTC')
            else:
                ax1.text(0.5, 0.5, 'Could not extract density profile', 
                        transform=ax1.transAxes, ha='center', va='center')
            
            # Plot 2: Altitude vs time contour
            if edp_cross is not None and edp_cross.shape[0] > 1 and edp_cross.shape[1] > 1:
                cs = ax2.contourf(ahr, aalt, edp_cross, levels=20, cmap='viridis')
                plt.colorbar(cs, ax=ax2, label='Electron Density (el/cm³)')
                ax2.set_xlabel('Hour (UTC)')
                ax2.set_ylabel('Altitude (km)')
                ax2.set_title(f'Electron Density vs Time\n{location_name}')
            else:
                ax2.text(0.5, 0.5, 'Time-altitude data not available', 
                        transform=ax2.transAxes, ha='center', va='center')
            
            plt.tight_layout()
            
            output_path = os.path.join(args.output, f'profiles_{location_name}_{timestamp}.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"✓ Electron density profiles saved: {output_path} ({size} bytes)")
            else:
                print(f"✗ Profiles plot failed to save")
                
        except Exception as e:
            print(f"✗ Profile creation failed: {e}")
    
    # List all PNG files created
    print("\n" + "="*50)
    try:
        files = [f for f in os.listdir(args.output) if f.endswith('.png')]
        print(f"PNG files created: {len(files)}")
        for f in sorted(files):
            filepath = os.path.join(args.output, f)
            size = os.path.getsize(filepath)
            print(f"  - {f} ({size:,} bytes)")
    except:
        print("Could not list output files")
    
    print(f"\nDone! Check {args.output} for your plots.")

if __name__ == "__main__":
    main()