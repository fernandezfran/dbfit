#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from database import read_database, SysQuery

database = read_database()

dcoeffs = []
for index, sys in database.iterrows():
    sysq = SysQuery(sys)

    isotherm = sysq.isotherm
    particle_size = sysq.particle_size
    dcoeff = sysq.dcoeff

    if not np.isnan(dcoeff):
        dcoeffs.append(dcoeff)

plt.boxplot(dcoeffs)
plt.yscale("log")
plt.show()
