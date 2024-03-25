#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import os
import pathlib

import matplotlib.pyplot as plt

import pandas as pd

PATH = pathlib.Path(os.path.join(os.path.abspath(os.path.dirname(__file__))))

MARKERS = {
    "Graphite": "s",
    "Graphite-Silicon": "8",
    "Silicon": "o",
    "LFP": "p",
    "LCO": "P",
    "LMO": "X",
    "NCA": "H",
    "NCO46": "D",
    "NMC": "d",
    "NMC111": "v",
    "NMC523": "<",
    "NMC622": ">",
    "NMC811": "^",
}

COLORS = {
    "Graphite": "tab:red",
    "Graphite-Silicon": "darkorange",
    "Silicon": "gold",
    "LFP": "indigo",
    "LCO": "lightslategray",
    "LMO": "forestgreen",
    "NCA": "mediumspringgreen",
    "NCO46": "palegreen",
    "NMC": "royalblue",
    "NMC111": "paleturquoise",
    "NMC523": "deepskyblue",
    "NMC622": "lightskyblue",
    "NMC811": "cornflowerblue",
}


def dcoeff_pred_vs_db(drange=(2e-16, 2e-7)):
    fig, ax = plt.subplots(figsize=(8, 5))

    df = pd.read_csv(PATH / "res" / "predictions.csv")
    for material, group in df.groupby("material"):
        ax.scatter(
            group["dcoeff_db"],
            group["dcoeff_pred"],
            label=material,
            marker=MARKERS[material],
            color=COLORS[material],
            zorder=2,
        )

    ax.plot(drange, drange, color="k", ls="--", alpha=0.5, zorder=1)

    ax.set_xlim(drange)
    ax.set_xscale("log")
    ax.set_xlabel(r"LiionDB $D$ [cm$^2$/s]")

    ax.set_ylim(drange)
    ax.set_yscale("log")
    ax.set_ylabel(r"Predicted $D$ [cm$^2$/s]")

    ax.legend(bbox_to_anchor=(1.02, 1.02))

    fig.tight_layout()
    fig.savefig(PATH / "res" / "predictions.png", dpi=600)


def socmax_pred_vs_actual():
    for fit_file in glob.glob(str(PATH / "res" / "fit-*")):
        df = pd.read_csv(fit_file)

        fig, ax = plt.subplots(figsize=(7, 5))

        ax.scatter(df["c_rate"], df["soc_max"])
        ax.plot(df["c_rate"], df["soc_max_pred"])

        ax.set_xscale("log")
        plt.show()


if __name__ == "__main__":
    dcoeff_pred_vs_db()
    # socmax_pred_vs_actual()
