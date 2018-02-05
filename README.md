<a href="https://github.com/zduguid">
    <img src="images/glider2.png" alt="glider_image" align="right" height="70">
</a>


# Slocum Glider Path Planner
The Slocum Glider is an autonomous underwater vehicle (AUV) that is specialized for long range research scenarios. To optimize the performance of the Slocum Glider, we choose to maximize its achievable range. The achievable range is maximized when the glider velocity is optimized subject to the hotel load scenario and the ocean current conditions. To explore this optimization problem, we examine a region of the Santa Barbara Basin, CA. To solve this optimization problem, we employ dynamic programming methods while using a Markov Decision Process (MDP) framework.  


## Table of Contents
- [Getting Started](#getting-started)
    - [Dependencies](#dependencies)
    - [Ocean Current Data](#ocean-current-data) 
- [Max Range Planner](#max-range-planner)
    - [To-Do](#to-do)
- [Acknowledgements](#acknowledgements)


## Getting Started 
To run this script, you will need to satisfy the following [Dependencies](#dependencies). To access ocean current information in either OPeNDAP or NCSS format, you will need to access [Ocean Current Data](#ocean-current-data).


### Dependencies 
* All scripts in this repository are written in ```Python3``` [(Python3 Download)](https://www.python.org/downloads/)
* ```netCDF4``` is used to retrieve ocean current information [(netCDF)](http://unidata.github.io/netcdf4-python/)
* ```matplotlib``` is used to create various plots [(matplotlib)](https://matplotlib.org)
* ```numpy``` is used to create array objects for graphing [(numpy)](http://www.numpy.org)
* ```Basemap``` works with ```matplotlib``` to create world map graphs [(Basemap)](https://matplotlib.org/basemap/)
* ```PyProj``` is a necessary dependency for ```Basemap``` [(PyProj)](https://pypi.python.org/pypi/pyproj?)


### Ocean Current Data
* HF Radar Network via [CORDC THREDDS](http://hfrnet.ucsd.edu/thredds/catalog.html)
* [OPeNDAP](http://hfrnet.ucsd.edu/thredds/dodsC/HFR/USWC/2km/hourly/RTV/HFRADAR,_US_West_Coast,_2km_Resolution,_Hourly_RTV_best.ncd.html) format (for Santa Barbara 2km)
* [NetcdfSubset](http://hfrnet.ucsd.edu/thredds/ncss/grid/HFR/USWC/2km/hourly/RTV/HFRADAR,_US_West_Coast,_2km_Resolution,_Hourly_RTV_best.ncd/dataset.html) format (for Santa Barbara 2km)


## Max Range Planner
Currently, the ```max_range_planner.py``` script merely plots ocean current information.

### To-Do
* implement MDP path planner that optimizes the achievable range of the Slocum Glider
* access OPeNDAP-hosted datasets to retrieve near-real-time ocean current information
* maintain backup ocean current data if OPeNDAP data retrieval is unsuccessful


## Author
* **Zach Duguid** - [zacharysupertramp](https://github.com/zduguid)


## Acknowledgements
* Computer Science and Artificial Intelligence Laboratory (CSAIL), MIT
* Deep Submergence Laboratory, WHOI
* National Science Foundation (NSF)
* Project Supervisor: Brian Williams
* Research Supervisor: Rich Camilli