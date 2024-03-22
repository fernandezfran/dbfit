#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import os
import pathlib
import re
import subprocess
import warnings

import numpy as np

import pandas as pd

import scipy.stats

import database.liiondb.functions.fn_db as fn_db

PATH = pathlib.Path(os.path.join(os.path.abspath(os.path.dirname(__file__))))

warnings.filterwarnings("ignore", category=RuntimeWarning)


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

    return database.reset_index(drop=True)


class SysQuery:
    def __init__(self, sys, socs="linspace"):
        self.sys = sys
        self.socs = np.linspace(1e-4, 0.9999) if socs == "linspace" else socs

    def _func_eval(self, func):
        with open(PATH / "_func.py", "wb") as binf:
            binf.write(func)

        subprocess.run(["black", "--quiet", PATH / "_func.py"])

        import database._func

        importlib.reload(database._func)

        try:
            yvals = database._func.function(self.socs)
        except TypeError:
            yvals = database._func.function(self.socs, T=298)

        os.remove(PATH / "_func.py")

        return yvals

    def _raw_data_value(self, value):
        return float(value)

    def _raw_data_array(self, array):
        return pd.DataFrame(
            data=[
                (x, y) for x, y in re.findall(r"\{([\d.]+),([\d.]+)\}", array)
            ],
            dtype=float,
        )

    @property
    def isotherm(self):
        if self.sys["isotherm_function"] is None:
            isotherm = self._raw_data_array(self.sys["isotherm"])
        else:
            voltage = self._func_eval(self.sys["isotherm_function"])
            isotherm = pd.DataFrame({0: self.socs, 1: voltage})

        return isotherm

    @property
    def particle_size(self):
        return 1e2 * self._raw_data_value(self.sys["particle_size"])

    @property
    def dcoeff(self):
        if self.sys["dcoeff_function"] is None:
            try:
                dcoeff = self._raw_data_value(self.sys["dcoeff"])
            except ValueError:
                dcoeffs = self._raw_data_array(self.sys["dcoeff"])
                try:
                    dcoeff = scipy.stats.gmean(dcoeffs.iloc[:, 1])
                except IndexError:
                    dcoeff = np.nan
        else:
            dcoeffs = self._func_eval(self.sys["dcoeff_function"])
            dcoeff = scipy.stats.gmean(dcoeffs)

        return 1e4 * dcoeff
