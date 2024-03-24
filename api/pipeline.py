#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pathlib

import galpynostatic as gp

import numpy as np

import pandas as pd

from database import read_database
from experiment import maximum_socs
from model import fit
from model import dcoeff_prediction, k0_prediction

PATH = pathlib.Path(os.path.join(os.path.abspath(os.path.dirname(__file__))))


def pipeline():
    database = read_database()

    c_rates = np.logspace(-2, 2)
    materials, dcoeffs_db, dcoeffs_pred, k0s_pred = [], [], [], []
    for index, sys in database.iterrows():
        material = sys["material"]

        density = gp.datasets.params.Electrode(material).density
        specific_capacity = gp.datasets.params.Electrode(
            material
        ).specific_capacity
        isotherm = pd.DataFrame(sys["isotherm"])
        particle_size = sys["particle_size"]
        dcoeff = sys["dcoeff"]

        soc_maxs = maximum_socs(
            c_rates,
            density,
            specific_capacity,
            isotherm,
            dcoeff,
            particle_size,
        )

        if soc_maxs.size == 0:
            continue

        greg = fit(c_rates[: soc_maxs.size], soc_maxs, particle_size)

        pd.DataFrame(
            {
                "c_rate": c_rates[: soc_maxs.size],
                "soc_max": soc_maxs,
                "soc_max_pred": greg.predict(
                    c_rates[: soc_maxs.size].reshape(-1, 1)
                ),
            }
        ).to_csv(PATH / "res" / f"fit-{index:02d}.csv", index=False)

        materials.append(material)
        dcoeffs_db.append(dcoeff)
        dcoeffs_pred.append(dcoeff_prediction(greg))
        k0s_pred.append(k0_prediction(greg))

    pd.DataFrame(
        {
            "material": materials,
            "dcoeff_db": dcoeffs_db,
            "dcoeff_pred": dcoeffs_pred,
            "k0s_pred": k0s_pred,
        }
    ).to_csv(PATH / "res" / "predictions.csv", index=False)


if __name__ == "__main__":
    pipeline()
