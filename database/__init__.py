#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib

import pandas as pd

import database.liiondb.functions.fn_db as fn_db

PATH = pathlib.Path(os.path.join(os.path.abspath(os.path.dirname(__file__))))


def read_database(merge_on=["doi", "material"]):
    dfndb, _ = fn_db.liiondb()

    with open(PATH / "query.sql", "r") as fsql:
        query = fsql.read()

    database = pd.read_sql(query, dfndb)

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

    return database
