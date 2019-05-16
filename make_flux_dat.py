# -*- coding: utf-8 -*-
"""
Created on Thu May 16 10:02:36 2019

Script for processing time series bathymetric data from the Colorado River at 
Diamond Creek as part of Ashley et al., "Estimating bedload flux from gage data
in sand bed rivers".

Requires:
    Python 3.6
    Anaconda 3
    qdune (https://github.com/tashley/qDune or pip install qdune)

The easiest approach is to run this script in spyder. Format data like the
example data included with qDune. Then change "datadir" to match the file
structure on your computer.

Tom Ashley
tashley22@gmail.com

"""

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 09:03:04 2017

@author: tashl
"""
import os
import _pickle as pickle
import numpy as np
from qdune import q
import matplotlib.pyplot as plt
import pandas as pd
import qdune

def save_object(obj, filename):
    with open(filename, 'wb') as outfile:
        pickle.dump(obj, outfile, -1)

def load_object(filename):
    with open(filename, 'rb') as infile:
        obj = pickle.load(infile)
    return obj

def make_fluxdat(qobj):
    """
    Vc is cellwise velocity
    Hc is  cellwise height

    code sums and then divides by the number of cells per unit width.

    Flux is reported in kg/s

    """
    return pd.DataFrame({'qb': (np.nansum(qobj.Vc * qobj.Hc * 0.5 * 0.65, 1)
                                * qobj.dy),
                         'wbed': (np.sum(~np.isnan(qobj.Vc), axis=1) * qobj.dy)
                         }, index = qobj.t)

    
#%% Process data and pickle results
    
cwd = os.getcwd()
datadir = cwd+os.sep+'data'
qfile = os.path.join(datadir, 'qobj.pkl')
qdatfile = os.path.join(datadir, 'qdatfile_w.csv')    

save = False              # Save intermediate calculations for gridding?
flow_azimuth = 158       # Degrees clockwise from east
dx = 0.1                 # Grid spacing in x direction
dy = 0.25                # Grid spacing in y direction
istart = 1800            # Crop location of upstream end of analysis region
iend = 2300              # Crop location of downstream end of analysis region
Lmax = 50/3              # Wavelength of maximum dune size (for fourier filter)
ref_xyz = 250            # Reference survey to determine grid extent


qobj = q(datadir, save, flow_azimuth, dx, dy, istart, iend, Lmax, ref_xyz=ref_xyz,
         datmin_grid=0.25, usepts=20, nanrad=2, datmin_geom=0.8, nsigma=2.5,
         maxslope=0.25, mincorr=0.8, Vmin=0.1/3600, Vmax=0.3/3600, dfracmin=0.001,
         dfracmax=0.2, minR2=0.75)

save_object(qobj, qfile)

#%% Save CSV
qobj = load_object(qfile)

qdat = make_fluxdat(qobj)
qdat.to_csv(qdatfile)