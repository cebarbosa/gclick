# -*- coding: utf-8 -*-
"""

Created on 01/02/2018

@Author: Carlos Eduardo Barbosa

Program to calculate Lick indices using lickmodels package.

"""
from __future__ import print_function, division

import os

import numpy as np
from astropy.table import Table, hstack
import matplotlib.pyplot as plt

from lick.lick import Lick
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
        err[i] = lick.classic
    err = np.nanstd(err, axis=0)
    return err

if __name__ == "__main__":
    # Setting the name of the directories for different users
    dir_ = ps.get_directories()
    nsim = 10
    ###########################################################################
    # Reading file with definition of Lick indices bands
    table = os.path.join(os.getcwd(), "lick/tables/bands.txt")
    bands = np.loadtxt(table, usecols=(2, 3, 4, 5, 6, 7,))
    names = np.loadtxt(table, usecols=(0,), dtype="S")
    colnames = [[_, "e_{}".format(_)] for _ in names]
    colnames = [item for sublist in colnames for item in sublist]
    ###########################################################################
    # Changing to directory with the data and getting names of the files
    os.chdir(os.path.join(dir_["data_dir"], "erros_sch05"))
    filenames = sorted(os.listdir("."))
    results = []
    for fname in filenames:
        wave, spec, sigma, sn = np.loadtxt(fname, unpack=True)
        lick = Lick(wave, spec, bands)
        lick.classic_integration()
        indices = lick.classic
        mcerr = mc_schiavon_err(wave, spec, sigma, bands, nsim=nsim)
        results.append(np.column_stack([indices, mcerr]).reshape(-1))
    names = Table([filenames], names=["spec"])
    results = Table(np.transpose(results).tolist(), names=colnames)
    results = hstack([names, results])
    output = os.path.join(dir_["tables_dir"], "lick_sch05_mc{}.fits".format(
        nsim))
    results.write(output, overwrite=True)