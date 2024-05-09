#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib

import galpynostatic as gp

import numpy as np

# this will be replaced by gp.simulation.GalvanostaticProfile in a future
# release
from lib._simulation import GalvanostaticProfile

PATH = pathlib.Path(os.path.join(os.path.abspath(os.path.dirname(__file__))))


def maximum_socs(
    c_rates,
    density,
    specific_capacity,
    isotherm,
    dcoeff,
    particle_size,
    index,
    material,
    k0=1e-7,
):
    soc_maxs = []
    for c_rate in c_rates:
        logxi = gp.utils.logxi(c_rate, dcoeff, k0)
        logell = gp.utils.logell(c_rate, particle_size, 3, dcoeff)

        gprof = GalvanostaticProfile(
            density,
            logxi,
            logell,
            specific_capacity=specific_capacity,
            isotherm=isotherm,
        )
        gprof.run()

        gprof.isotherm_df.to_csv(
            PATH / "res" / f"_sim-{index:02d}-{material}-{c_rate:.4f}.csv",
            index=False,
        )

        soc_maxs.append(np.max(gprof.isotherm_df["SOC"]))

    soc_maxs = np.array(soc_maxs)
    mask = ~np.isnan(soc_maxs)

    return soc_maxs[mask]
