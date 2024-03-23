#!/usr/bin/env python
# -*- coding: utf-8 -*-
import galpynostatic as gp

import numpy as np

# this will be replaced by gp.simulation.GalvanostaticProfile in a future
# release
from lib._simulation import GalvanostaticProfile


def maximum_socs(
    c_rates,
    density,
    specific_capacity,
    isotherm,
    dcoeff,
    particle_size,
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

        soc_maxs.append(np.max(gprof.isotherm_df["SOC"]))

    soc_maxs = np.array(soc_maxs)
    mask = ~np.isnan(soc_maxs)

    return soc_maxs[mask]
