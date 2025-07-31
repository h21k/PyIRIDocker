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

# 2025 NASA Heliolab Ionosphere - Thermosphere Team<br> 

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
              

