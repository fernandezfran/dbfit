#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import liiondb.functions.fn_db as fn_db

warnings.filterwarnings("ignore", category=RuntimeWarning)

dfndb, _ = fn_db.liiondb()

with open("query.sql", "r") as fsql:
    query = fsql.read()

database = pd.read_sql(query, dfndb)

merge_on = ["doi", "material"]

database = (
    database.merge(database, on=merge_on)
    .query("parameter_x != parameter_y")
    .merge(database, on=merge_on)
    .query("parameter != parameter_x & parameter != parameter_y")
    .query(
        "parameter_x == 'half cell ocv' & "
        "parameter_y == 'particle radius' & "
        "parameter == 'diffusion coefficient'"
    )
)
database = database.rename(
    columns={
        "raw_data_x": "isotherm",
        "raw_data_y": "particle_size",
        "raw_data": "dcoeff",
        "function_x": "isotherm_function",
        "function": "dcoeff_function",
    },
)[
    [
        "doi",
        "material",
        "isotherm",
        "particle_size",
        "dcoeff",
        "isotherm_function",
        "dcoeff_function",
    ]
]
database.reset_index(drop=True, inplace=True)

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
                [float(y) for _, y in re.findall(r"\{([\d.]+),([\d.]+)\}", dcoeff)]
            )
    else:
        func = database.iloc[index]["dcoeff_function"]
        exec(func)
        try:
            dcoeff = 1e4 * np.mean(function(socs))
        except TypeError:
            dcoeff = 1e4 * np.mean(function(socs, T=298))
