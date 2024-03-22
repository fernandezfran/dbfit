#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

import numpy as np

from database import CleanSysData, read_database

database = read_database()

dcoeffs = []
for index, sys in database.iterrows():
    sys_data = CleanSysData(sys)

    isotherm = sys_data.isotherm
    particle_size = sys_data.particle_size
    dcoeff = sys_data.dcoeff

    if not np.isnan(dcoeff):
        dcoeffs.append(dcoeff)

plt.boxplot(dcoeffs)
plt.yscale("log")
plt.show()
