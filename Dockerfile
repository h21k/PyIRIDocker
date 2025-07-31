# Dockerfile - PyIRI Full Implementation with Global Mapping
# Created during the 2025 NASA Heliolab Ionosphere Team Project
# Created by Frank Soboczenski, PhD 
# Date: July, 31st, 2025 
# Version: 1.01
####

FROM python:3.10-slim

# Use LABEL instead of deprecated MAINTAINER
LABEL maintainer="frank soboczenski <frank.soboczenski@gmail.com>"
LABEL version="2025.1-pyIRI-full"
LABEL description="NASA Heliolab Team Ionosphere - Complete PyIRI Docker Image with Global Mapping"

# Install system dependencies including cartographic libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gfortran \
        make \
        git \
        build-essential \
        wget \
        curl \
        libproj-dev \
        proj-data \
        proj-bin \
        libgeos-dev \
        libgeos++-dev \
        libgeos-c1v5 \
        libudunits2-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone the repo and submodules (for IRI2020 Fortran code)
RUN git clone --recurse-submodules https://github.com/victoriyaforsythe/PyIRI.git

# Set working directory to the cloned repository
WORKDIR /app/PyIRI

# Install build dependencies and PyIRI requirements
RUN pip install --no-cache-dir numpy build

# Build and install PyIRI
RUN python -m build . && \
    pip install dist/*.whl

# Install comprehensive dependencies for plotting, mapping, and data handling
RUN pip install --no-cache-dir \
    matplotlib \
    pandas \
    scipy \
    cartopy \
    netcdf4 \
    xarray \
    requests \
    pillow

# Create output directory for plots and data
RUN mkdir -p /app/output

# Copy all PyIRI runner scripts
COPY pyiri_runner.py /app/pyiri.py
COPY pyiri_year_plot.py /app/pyiri_year_plot.py
COPY pyiri_year_daily.py /app/pyiri_year_daily.py

# Set working directory back to /app
WORKDIR /app

# Make the scripts executable
RUN chmod +x /app/pyiri.py /app/pyiri_year_plot.py /app/pyiri_year_daily.py

# Set matplotlib to use non-interactive backend
ENV MPLBACKEND=Agg

# Default command - show help
CMD ["python", "pyiri.py", "--help"]