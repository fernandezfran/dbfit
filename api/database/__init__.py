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


class CleanSysData:
    def __init__(self, sys):
        self.sys = sys

    def _raw_data_value(self, value):
        return float(value)

    def _raw_data_array(self, array):
        return pd.DataFrame(
            data=[
                (x, y) for x, y in re.findall(r"\{([\d.]+),([\d.]+)\}", array)
            ],
            dtype=float,
        )

    def _socs_to_eval(self, input_range):
        self.socs_ = np.linspace(
            float(input_range.lower), float(input_range.upper)
        )

    def _func_eval(self, func):
        with open(PATH / "_func.py", "wb") as binf:
            binf.write(func)

        subprocess.run(["black", "--quiet", PATH / "_func.py"])

        import database._func

        importlib.reload(database._func)

        try:
            yvals = database._func.function(self.socs_)
        except TypeError:
            yvals = database._func.function(self.socs_, T=298)

        os.remove(PATH / "_func.py")

        return yvals

    @property
    def particle_size(self):
        return 2.0e2 * self._raw_data_value(self.sys["particle_size"])

    @property
    def dcoeff(self):
        if self.sys["dcoeff"] == "see function":
            self._socs_to_eval(self.sys["dcoeff_range"])
            dcoeffs = self._func_eval(self.sys["dcoeff_function"])
            dcoeff = scipy.stats.gmean(dcoeffs)
        else:
            try:
                dcoeff = self._raw_data_value(self.sys["dcoeff"])
            except ValueError:
                dcoeffs = self._raw_data_array(self.sys["dcoeff"])
                try:
                    dcoeff = scipy.stats.gmean(dcoeffs.iloc[:, 1])
                except IndexError:
                    dcoeff = np.nan

        return 1.0e4 * dcoeff

    @property
    def isotherm(self):
        if self.sys["isotherm"] == "see function":
            self._socs_to_eval(self.sys["isotherm_range"])
            voltage = self._func_eval(self.sys["isotherm_function"])
            mask = np.isfinite(voltage)
            isotherm = pd.DataFrame({0: self.socs_[mask], 1: voltage[mask]})
        else:
            isotherm = self._raw_data_array(self.sys["isotherm"])

        return isotherm


def read_database():
    dfndb, _ = fn_db.liiondb()

    with open(PATH / "query.sql", "r") as fsql:
        query = fsql.read()

    database = pd.read_sql(query, dfndb)

    for index, sys in database.iterrows():
        sys_data = CleanSysData(sys)
        database.loc[index, "particle_size"] = sys_data.particle_size
        database.loc[index, "dcoeff"] = sys_data.dcoeff
        database.loc[index, "isotherm"] = sys_data.isotherm.to_numpy()

    database = database.dropna(subset=["particle_size", "dcoeff", "isotherm"])
    database = database.reset_index(drop=True)

    return database[["material", "particle_size", "dcoeff", "isotherm", "doi"]]
