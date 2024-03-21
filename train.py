#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import warnings

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
    },
)[["doi", "material", "isotherm", "particle_size", "dcoeff"]]

for _, sys in database.iterrows():
    isotherm = [
        (float(x), float(y))
        for x, y in re.findall(r"\{([\d.]+),([\d.]+)\}", sys["isotherm"])
    ]
    isotherm = pd.DataFrame(isotherm, columns=["capacity", "voltage"])

    particle_size = 1e2 * float(sys["particle_size"])

    dcoeff = sys["dcoeff"]
    try:
        dcoeff = float(dcoeff)
    except ValueError:
        dcoeff = np.mean(
            [float(y) for _, y in re.findall(r"\{([\d.]+),([\d.]+)\}", dcoeff)]
        )
