# -*- coding: utf-8 -*-
"""

Created on 01/02/2018

@Author: Carlos Eduardo Barbosa

Program to calculate Lick indices using lickmodels package.

"""
from __future__ import print_function, division

import os

import numpy as np
import matplotlib.pyplot as plt

from pysps.lick import Lick
import project_settings as ps

def mc_schiavon_err(wave, flux, sigma, bands, nsim=10):
    """ Monte Carlo simulations to determine error in Lick indices. """
    npix = len(flux)
    pert = np.zeros((npix, nsim))
    for i in np.arange(npix):
        pert[i] = np.random.normal(0, np.abs(sigma[i]), nsim)
    aflux = np.repeat(flux, nsim).reshape(npix, nsim).T
    sim = aflux + pert.T
    err = np.zeros((nsim, 25))
    for i in np.arange(nsim):
        lick = Lick(wave, sim[i], bands)
        lick.classic_integration()
        lick.classic_integration()
        err[i] = lick.classic
    err = np.nanstd(err, axis=0)
    return err

if __name__ == "__main__":
    # Setting the name of the directories for different users
    dir_ = ps.get_directories()
    ###########################################################################
    # Reading file with definition of Lick indices bands
    table = os.path.join(os.getcwd(), "pysps/tables/bands.txt")
    bands = np.loadtxt(table, usecols=(2, 3, 4, 5, 6, 7,))
    ###########################################################################
    # Changing to directory with the data and getting names of the files
    os.chdir(os.path.join(dir_["data_dir"], "schiavon2005"))
    filenames = sorted([_ for _ in os.listdir(".") if _.endswith("txt")])
    for fname in filenames:
        wave, spec, var, sn = np.loadtxt(fname, unpack=True)
        sigma = np.sqrt(var)
        lick = Lick(wave, spec, bands)
        lick.classic_integration()
        mcerr = mc_schiavon_err(wave, spec, sigma, bands)
        break