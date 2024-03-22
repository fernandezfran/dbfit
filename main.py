#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import os
import re
import subprocess
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from database import read_database


class SysQuery:
    def __init__(self, sys, socs="linspace"):
        self.sys = sys
        self.socs = np.linspace(0, 1) if socs == "linspace" else socs

    def _func_eval(self, func):
        with open("_func.py", "wb") as binf:
            binf.write(func)

        subprocess.run(["black", "--quiet", "_func.py"])

        import _func

        importlib.reload(_func)

        try:
            yvals = _func.function(self.socs)
        except TypeError:
            yvals = _func.function(self.socs, T=298)

        os.remove("_func.py")

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
                    dcoeff = np.mean(dcoeffs.iloc[:, 1])
                except IndexError:
                    dcoeff = np.nan
        else:
            dcoeffs = self._func_eval(self.sys["dcoeff_function"])
            dcoeff = np.mean(dcoeffs)

        return 1e4 * dcoeff


warnings.filterwarnings("ignore", category=RuntimeWarning)

database = read_database()

for index, sys in database.iterrows():
    sysq = SysQuery(sys)

    isotherm = sysq.isotherm
    particle_size = sysq.particle_size
    dcoeff = sysq.dcoeff
