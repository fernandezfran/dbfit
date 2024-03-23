#!/usr/bin/env python
# -*- coding: utf-8 -*-
import galpynostatic as gp

import matplotlib.pyplot as plt

import numpy as np

from database import CleanSysData, read_database
from experiment.simulate import maximum_socs

database = read_database()

c_rates = np.logspace(-2, 2)
for index, sys in database.iterrows():
    material = sys["material"]
    sys_data = CleanSysData(sys)

    density = gp.datasets.params.Electrode(material).density
    specific_capacity = gp.datasets.params.Electrode(
        material
    ).specific_capacity
    isotherm = sys_data.isotherm
    particle_size = sys_data.particle_size
    dcoeff = sys_data.dcoeff

    if np.isnan(dcoeff):
        continue

    soc_maxs = maximum_socs(
        c_rates, density, specific_capacity, isotherm, dcoeff, particle_size
    )
    print(soc_maxs)
