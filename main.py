#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from database import read_database

warnings.filterwarnings("ignore", category=RuntimeWarning)

database = read_database()

socs = np.linspace(0, 1, num=100)

for index, sys in database.iterrows():
    if sys["isotherm_function"] is None:
        isotherm = [
            (float(x), float(y))
            for x, y in re.findall(r"\{([\d.]+),([\d.]+)\}", sys["isotherm"])
        ]
        isotherm = pd.DataFrame(isotherm, columns=["capacity", "voltage"])
    else:
        func = database.iloc[index]["isotherm_function"]
        exec(func)
        isotherm = pd.DataFrame({"capacity": socs, "voltage": function(socs)})

    particle_size = 1e2 * float(sys["particle_size"])

    if sys["dcoeff_function"] is None:
        dcoeff = sys["dcoeff"]
        try:
            dcoeff = 1e4 * float(dcoeff)
        except ValueError:
            dcoeff = 1e4 * np.mean(
                [
                    float(y)
                    for _, y in re.findall(r"\{([\d.]+),([\d.]+)\}", dcoeff)
                ]
            )
    else:
        func = database.iloc[index]["dcoeff_function"]
        exec(func)
        try:
            dcoeff = 1e4 * np.mean(function(socs))
        except TypeError:
            dcoeff = 1e4 * np.mean(function(socs, T=298))
