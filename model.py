#!/usr/bin/env python
# -*- coding: utf-8 -*-
import galpynostatic as gp


def fit(c_rates, soc_maxs, particle_size):
    greg = gp.model.GalvanostaticRegressor(d=particle_size)
    return greg.fit(c_rates.reshape(-1, 1), soc_maxs)


def dcoeff_prediction(greg):
    return greg.dcoeff_


def k0_prediction(greg):
    return greg.k0_
