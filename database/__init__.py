#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import os
import pathlib
import re
import subprocess
import warnings

import galpynostatic as gp

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

    return pd.read_sql(query, dfndb)


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
    def isotherm(self):
        if self.sys["isotherm_function"] is None:
            isotherm = self._raw_data_array(self.sys["isotherm"])
        else:
            self._socs_to_eval(self.sys["isotherm_range"])
            isotherm = pd.DataFrame(
                {
                    0: self.socs_,
                    1: self._func_eval(self.sys["isotherm_function"]),
                }
            )

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
            self._socs_to_eval(self.sys["dcoeff_range"])
            dcoeffs = self._func_eval(self.sys["dcoeff_function"])
            dcoeff = scipy.stats.gmean(dcoeffs)

        return 1e4 * dcoeff

    @property
    def density(self):
        return gp.datasets.params.Electrode(self.sys["material"]).density

    @property
    def specific_capacity(self):
        return gp.datasets.params.Electrode(
            self.sys["material"]
        ).specific_capacity
