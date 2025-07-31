<img width="200" height="200" src="https://.png" alt="Black circle " title="PyIRI Logo" style="float:left;">

# PyIRIDocker 
A docker version of PyIRI - A Python implementation of the International Reference Ionosphere (IRI) model that evaluates the electron density and associated ionospheric parameters on the entire given global grid and for the entire day simultaneously.

This is a Docker version of PyIRI developeed by Victoriya V. Forsythe https://github.com/victoriyaforsythe : [PyIRI Main Repository](https://github.com/victoriyaforsythe/PyIRI)<br> 

The PyIRI documentation can be found here: [PyIRI Documentation](https://pyiri.readthedocs.io/en/latest/)<br>

PyIRI info:<br>
[![PyPI Package latest release](https://img.shields.io/pypi/v/PyIRI.svg)](https://pypi.org/project/PyIRI/)
[![Build Status](https://github.com/victoriyaforsythe/PyIRI/actions/workflows/main.yml/badge.svg)](https://github.com/victoriyaforsythe/PyIRI/actions/workflows/main.yml)
[![Documentation Status](https://readthedocs.org/projects/pyiri/badge/?version=latest)](https://pyiri.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8235173.svg)](https://doi.org/10.5281/zenodo.8235173)
[![Coverage Status](https://coveralls.io/repos/github/victoriyaforsythe/PyIRI/badge.svg?branch=main)](https://coveralls.io/github/victoriyaforsythe/PyIRI?branch=main)

## 2025 NASA Heliolab Ionosphere - Thermosphere Team<br> 

[Thomas Trikalinos](https://vivo.brown.edu/display/ttrikali) Center for Evidence-based Medicine, Brown University, Providence, USA<br>
[Joel Kuiper](https://joelkuiper.eu/) Vortext Systems, Groningen, Netherlands<br>
[Randolph G Bias](https://www.ischool.utexas.edu/~rbias/site/) School of Information, University of Texas at Austin, Austin, USA<br>
[Byron C Wallace](http://www.byronwallace.com/) College of Computer and Information Science, Northeastern University, Boston, USA<br>
[Iain J Marshall](https://kclpure.kcl.ac.uk/portal/iain.marshall.html) School of Population Health and Life Sciences, King's College London, London, UK<br>
[Frank Soboczenski](https://h21k.github.io/) School of Population Health and Life Sciences, King's College London, London, UK [PyIRIDocker Author] <br>

## Structure of the repository

File Structure:<br> 

+ `Dockerfile` (Dockerfile pulling PyIRI from its repository)<br>
+ `pyiri_runner.py` (PyIRI Simple Runner Script with Plots that Save to a Designated Output Directory)<br>
+ `pyiri_year_plot.py` (Generates plots with daily resolution similar to PyIRI_year_run.ipynb)<br>
+ `pyiri_year_daily.py` (Generates plots similar to PyIRI_year_run.ipynb showing F10.7 input and NmF2 output)<br>
              
## Run instructions

## Dockerhub
```
docker run -it angrycoffeemonster/pyiridocker:101
```

## Pull repo & build locally 
```
git clone https://github.com/h21k/PyIRIDocker.git
cd PyIRIDocker
docker build -t pyiridocker .

# make the directory to store the ouput files outside the docker container:
mkdir ~/pyiri_output #in MAC this will make a directory called pyiri_output in the root user directory that we pass below
```

## Helpfile
```
docker run -it --rm pyiridocker python pyiri.py --help
```

## Single Location Examples
```
# Basic single location (New York)
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --lat 40.7128 --lon -74.0060

# With specific parameters
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --lat 51.5074 --lon -0.1278 --parameters foF2 hmF2 NmF2

# With daily mode (includes electron density profiles)
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --lat 35.6762 --lon 139.6503 --daily

# With electron density profiles visualization
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --lat -33.8688 --lon 151.2093 --daily --profiles
```

## Global Map Examples
```
# Basic global map (10° resolution)
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --global-map --resolution 10

# High resolution global map (5°)
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --global-map --resolution 5 --parameters foF2 hmF2 NmF2

# Global map with vTEC calculation
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --global-map --daily --vtec --resolution 10

# Everything enabled for global map
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --global-map --daily --vtec --parameters foF2 hmF2 NmF2 \
  --resolution 10 --year 2020 --month 4 --day 15 --hour 12 --f107 100
```

## Special Location Examples
```
# Equator
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --lat 0 --lon 0 --daily --profiles

# North Pole
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --lat 90 --lon 0

# Auroral Zone
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --lat 65 --lon -150 --daily --vtec

# Everything enabled for global map
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --global-map --daily --vtec --parameters foF2 hmF2 NmF2 \
  --resolution 10 --year 2020 --month 4 --day 15 --hour 12 --f107 100
```

## Different Times and Solar Activity
```
# Nighttime (00:00 UTC)
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --lat 40 --lon -100 --hour 0

# Solar Minimum Conditions
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --global-map --f107 70 --resolution 10

# Solar Maximum Conditions
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --global-map --f107 200 --resolution 10
```

## Complex Examples
```
# Full analysis for a specific location
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --lat 52.5200 --lon 13.4050 \
  --daily --profiles --vtec \
  --parameters foF2 hmF2 NmF2 \
  --year 2021 --month 6 --day 21 --hour 14 --f107 150

# Global ionospheric state during geomagnetic storm
docker run -it --rm -v ~/pyiri_output:/app/output pyiridocker \
  python pyiri.py --global-map --daily --vtec \
  --parameters foF2 hmF2 NmF2 \
  --resolution 5 --f107 180 \
  --year 2023 --month 3 --day 24 --hour 18
```


Parameter Options
Location Parameters

--lat: Latitude (-90 to 90)
--lon: Longitude (-180 to 180)
--global-map: Generate global map instead of single location
--resolution: Grid resolution for global maps (degrees, default: 5.0)

Time Parameters

--year: Year (default: 2020)
--month: Month (1-12, default: 4)
--day: Day (1-31, default: 15)
--hour: Hour UTC (0-23, default: 12)

Solar Activity

--f107: F10.7 solar flux index (default: 100)

Low activity: 70
Medium activity: 100-150
High activity: 200+

Output Parameters

--parameters: Space-separated list of parameters to plot

foF2: F2 critical frequency
hmF2: F2 peak height
NmF2: F2 peak density
Use all for all parameters

Processing Modes

--daily: Use daily parameters (enables electron density profiles)
--profiles: Create electron density profile plots
--vtec: Calculate and plot vertical Total Electron Content

Output

--output: Output directory (default: /app/output)

Output Files
The script generates PNG files with names following this pattern:

Single location: {parameter}_{lat}N_{lon}E_{timestamp}.png
Global maps: {parameter}_Global_{resolution}deg_{timestamp}.png
Time series: timeseries_{location}_{timestamp}.png
Profiles: profiles_{location}_{timestamp}.png
vTEC: vTEC_{location}_{timestamp}.png

Tips

Start with low resolution (10-15°) for global maps to test quickly
Use --daily mode to enable electron density profiles and vTEC
The --profiles flag requires --daily to be set
Higher F10.7 values represent more active solar conditions
Processing time increases significantly with resolution and when using --daily mode
