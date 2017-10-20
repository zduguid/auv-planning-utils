# /usr/local/lib/python3.6
#
# - Determines glider range based on battery capacity and ocean current conditions
# - Model uses MDP as a dynamic programming approach 
#
# Author: Zach Duguid
# Last Updated: 10/20/2017


import math
import numpy as np
from netCDF4 import Dataset
import matplotlib
import warnings
import matplotlib.cbook
from matplotlib import pyplot as plt 
import matplotlib.font_manager as font_manager
import mpl_toolkits
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.patches import Polygon


class SlocumGlider(object):
    def __init__(self):
        ''' initialize glider model object and define model parameters  
        '''
        # capacity parameters
        self.capacity_li_pri = 12167        # non-rechargable
        self.capacity_li_sec = 3200         # rechargable 
        self.constant_transit_pwr = 5.5     # total transit power [W], assumes 5W mass spectrometer and 0.5W vehicle
        self.constant_survey_pwr = 12.5     # total survey power [W], assumes 12W mass spectrometer and 0.5W vehicles 
        self.c1 = 0.5213                    # coefficient from graphical fit
        self.c2 = 0.3467                    # coefficient from graphical fit

        # graphing parameters   
        self.major_line_width = 3           # width of thick graph lines 
        self.minor_line_width = 1           # width of small graph lines
        self.inset_size = '20%'             # size of inset map
        self.resolution = 'i'               # map resolution
        self.R = 6378.1                     # radius of the Earth [km]
        self.base_land = 'peachpuff'        # base map land color
        self.base_water = 'powderblue'      # base map water color
        self.base_lines = 0.2               # base map line width
        self.inset_land = 'white'           # inset map land color 
        self.inset_water = 'grey'           # inset map water color 
        self.inset_box = 'red'              # inset map box color 

        self.title_font = {'fontname':'Arial',                  # specify Title font
                           'size':'16',     
                           'color':'black', 
                           'weight':'bold'}
        self.axis_font = {'fontname':'Arial',                   # specify Axis font
                          'size':'16',
                          'color':'black',
                          'weight':'bold'} 
        self.font_prop = font_manager.FontProperties(size=14)   # specify legend font


    def get_prop_power(self, v):
        ''' determines propulsive power needed to achieve v, the through-water-speed
        '''
        return((v/self.c1)**(1/self.c2))


    def get_lat_lon(self, lat1, lon1, dist, brng):
        ''' determines new lat-lon coordinates given a reference cooridnate pair, a distance, and a bearing angle
            :important note:
                for this formula to work, all terms must be in radians 
        '''
        lat2 = math.asin((math.sin(lat1) * math.cos(dist/self.R)) + (math.cos(lat1) * math.sin(dist/self.R) * math.cos(brng)))
        dlon = math.atan2((math.sin(brng) * math.sin(dist/self.R) * math.cos(lat1)), (math.cos(dist/self.R) - math.sin(lat1) * math.sin(lat2)))
        lon2 = ((lon1 - dlon + math.pi) % (2*math.pi)) - math.pi
        return(lat2,lon2)


    def get_ocean_data(self, fname):
        ''' reads in ocean current information from fname and stores data in relevant format
            :data of interest: 
                U = surface_eastward_sea_water_velocity
                V = surface_northward_sea_water_velocity
                C = magnitude_of_sea_water_velocty
                X = degrees_east
                Y = degrees_north
        '''
        # read in the file
        self.dataset = Dataset(fname, 'r', format='NETCDF4')

        # record number of columns and number of rows for the dataset array
        self.lon_len = self.dataset.variables['lon'].shape[0]
        self.lat_len = self.dataset.variables['lat'].shape[0]

        # store U, V, X, Y arrays in glider object, convert NaN to 0
        with np.errstate(invalid='ignore'):
            self.U = np.nan_to_num(self.dataset['u'][0])
            self.V = np.nan_to_num(self.dataset['v'][0])
        self.C = (self.U**2 + self.V**2)**0.5;
        self.X = np.array([self.dataset.variables['lon'] for i in range(self.lat_len)])
        self.Y = np.array([[self.dataset['lat'][i] for j in range(self.lon_len)] for i in range(self.lat_len)])


    def get_map(self):
        ''' creates a visual display of the glider range overlayed on the world map
        '''
        # ignore matplotlib deprecation warnings
        warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

        # draw basemap
        fig = plt.figure(figsize=(12.5,6.5))
        ax = fig.add_subplot(111)
        bmap = Basemap(projection='merc', llcrnrlon=self.llcrnrlon, llcrnrlat=self.llcrnrlat, urcrnrlon=self.urcrnrlon, urcrnrlat=self.urcrnrlat, resolution=self.resolution, ax=ax)
        bmap.fillcontinents(color=self.base_land, lake_color=self.base_water)
        bmap.drawcountries(linewidth=self.base_lines)
        bmap.drawstates(linewidth=self.base_lines)
        bmap.drawcoastlines(linewidth=self.base_lines)
        bmap.drawmapboundary(fill_color=self.base_water)
        plt.title('Slocum Glider in Santa Barbara Basin, CA', **self.title_font)

        # create axes for inset map
        axin = inset_axes(bmap.ax, width=self.inset_size, height=self.inset_size, loc=4)

        # draw inset map  
        omap = Basemap(projection='ortho', lat_0=self.llcrnrlat, lon_0=self.llcrnrlon, ax=axin, anchor='NE')
        omap.drawcountries(color=self.inset_land)
        omap.fillcontinents(color=self.inset_water)               
        bx, by = omap(bmap.boundarylons, bmap.boundarylats)
        xy = list(zip(bx,by))
        mapboundary = Polygon(xy, edgecolor=self.inset_box, linewidth=self.major_line_width, fill=False, zorder=5)
        omap.ax.add_patch(mapboundary)

        # draw ocean currents
        bmap.quiver(glider.X, glider.Y, glider.U, glider.V, glider.C, cmap='viridis', scale=15, latlon=True)

        # show the plot
        plt.show()


if __name__ == '__main__':
    # initialize Glider Model object 
    glider = SlocumGlider()

    # coordinates of Santa Barbara Basin in DublinCore format
    westlimit = -120.95
    southlimit = 33.72
    eastlimit = -118.66
    northlimit = 34.62

    # coordinates in Mercator map format, plotting with Basemap
    glider.llcrnrlon = westlimit
    glider.llcrnrlat = southlimit
    glider.urcrnrlon = eastlimit
    glider.urcrnrlat = northlimit

    # file name of ocean current data
    fname = 'data/RTV_HFRADAR,_US_West_Coast,_2km_Resolution,_Hourly_RTV_best.nc4'
    glider.get_ocean_data(fname)

    # plot the map
    glider.get_map()
    