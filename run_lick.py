# -*- coding: utf-8 -*-
"""

Created on 06/12/2016

@Author: Carlos Eduardo Barbosa

Program to calculate Lick indices using lickmodels package.

"""

import os

import numpy as np
import pyfits as pf
import matplotlib.pyplot as plt

from lickpy.lick import Lick
import project_settings as ps

def wavelength_array(h):
    """ Produces array for wavelenght of a given array. """
    w0 = h["CRVAL1"]
    deltaw = h["CDELT1"]
    pix0 = h["CRPIX1"]
    npix =h["NAXIS1"]
    return w0 + deltaw * (np.arange(npix) + 1 - pix0)

if __name__ == "__main__":
    # Setting the name of the directories for different users
    dir_ = ps.get_directories()
    ###########################################################################
    # Reading file with definition of Lick indices bands
    table = os.path.join(os.getcwd(), "lickpy/tables/bands.txt")
    bands = np.loadtxt(table, usecols=(2, 3, 4, 5, 6, 7,))
    ###########################################################################
    # Changing to directory with the data and getting names of the files
    os.chdir(os.path.join(dir_["data_dir"]))
    filenames = sorted([_ for _ in os.listdir(".") if _.endswith("fits")])
    # Removing aux files
    filenames = [_ for _ in filenames if not _.endswith("aux.fits")]
    for fname in filenames:
        spec = pf.getdata(fname)
        header = pf.getheader(fname)
        wave = wavelength_array(header)
        plt.plot(wave, spec)
        lick = Lick(wave, spec, bands)
        lick.classic_integration()
        print lick.classic # These are the values of the Lick indices