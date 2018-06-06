# -*- coding: utf-8 -*-
""" 

Created on 06/06/18

Author : Carlos Eduardo Barbosa

Model of SSPs using Lick indices

"""
from __future__ import print_function, division

import os

import numpy as np
from astropy.table import Table, hstack, vstack
from scipy.interpolate import LinearNDInterpolator
import pymc

import context as context


class SSPs():
    """ Produces a linearly-interpolated model. """

    def __init__(self, model_table, indices=None):
        self.indices = indices if indices is not None else np.arange(25)
        self.interpolate(model_table)
        return

    def interpolate(self, model_table):
        data = Table.read(model_table, format="fits")
        vars = np.column_stack([data["T"], data["Z"], data["Alpha"]])
        lick = np.column_stack([data[col] for col in data.colnames[3:]])
        self.model = LinearNDInterpolator(vars, lick)
        self.ages_lims = [data["T"].min(), data["T"].max()]
        self.metal_lims = [data["Z"].min(), data["Z"].max()]
        self.alpha_lims = [data["Alpha"].min(), data["Alpha"].max()]
        return

    def fn(self, age, metallicity, alpha):
        return self.model(age, metallicity, alpha)[self.indices]

    def __call__(self, *args):
        return self.fn(*args)


def prepare_table(redo=False):
    """ Prepare a table for the SSP model fitting. """
    outtable = "tables/vazdekis2016_lick.fits"
    if os.path.exists(outtable) and not redo:
        return outtable
    tables = ["miles_solar_lick.txt", "miles_alpha_lick.txt"]
    newtables = []
    for table in tables:
        data = Table.read("tables/{}".format(table), format="ascii")
        Zs, Ts, As = [], [], []
        for filename in data["Models"]:
            Z = float(filename.split("Z")[1].split("T")[0].replace("m",
                      "-").replace("p", "+"))
            T = float(filename.split("T")[1].split("_")[0])
            A = float(filename.split("Ep")[1].split(".fits")[0])
            Zs.append(Z)
            Ts.append(T)
            As.append(A)
        pars = Table([Zs, Ts, As], names=["Z", "T", "Alpha"])
        newtables.append(hstack((pars, data[data.colnames[1:]])))
    newtable = vstack(newtables)
    newtable.write(outtable, overwrite=True)
    return outtable

def model_lick(lick, errors, ssps, dbname, redo=False):
    """ Routine that performs the Bayesian modeling using MCMC."""
    if os.path.exists(dbname) and not redo:
        return
    # Defining simple priors for the variables
    age_dist = pymc.Uniform(name="age_dist", lower=ssps.ages_lims[0],
                            upper=ssps.ages_lims[1])
    metal_dist = pymc.Uniform(name="metal_dist", lower=ssps.metal_lims[0],
                              upper=ssps.ages_lims[1])
    alpha_dist = pymc.Uniform(name="alpha_dist", lower=ssps.alpha_lims[0],
                              upper=ssps.alpha_lims[1])

    @pymc.deterministic()
    def ssp1(age=age_dist, metal=metal_dist, alpha=alpha_dist):
        return ssps(age, metal, alpha)

    likelihood = pymc.Cauchy(name="like", alpha=ssp1, beta=errors,
                    value=lick, observed=True)

    model = pymc.Model([likelihood, age_dist, metal_dist, alpha_dist])
    mcmc = pymc.MCMC(model, db="txt", dbname=dbname)
    mcmc.sample(20000, 1000, 4)
    mcmc.db.close()
    mcmc.summary()
    return


if __name__ == "__main__":
    model_table = prepare_table(redo=False)
    ssps = SSPs(model_table)
    dirs = context.get_directories()
    table = os.path.join(dirs["tables_dir"], "lick_sch05_mc200.fits")
    data = Table.read(table, format="fits")
    outdir = os.path.join(dirs["home"], "dbs")
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for gc in data:
        indices = [_ for _ in gc.colnames[1:] if not _.startswith("e_")]
        e_indices = ["e_{}".format(_) for _ in indices]
        lick = np.array([gc[index] for index in indices])
        errors = np.array([gc[index] for index in e_indices])
        dbname = os.path.join(outdir, "{}.db".format(gc["spec"]))
        model_lick(lick, errors, ssps, dbname)