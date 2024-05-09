#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import os
import pathlib

import galpynostatic as gp

import matplotlib.pyplot as plt

import numpy as np

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


def dcoeff_pred_vs_db(drange=(1e-16, 1e-6)):
    plt.rcParams.update({"font.size": 12})

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


def simulations():
    plt.rcParams.update({"font.size": 12})

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(5, 8))

    for index, material, i, ax in zip(
        ["06", "24"], ["Graphite", "LFP"], ["b", "a"], axes[::-1]
    ):
        df = pd.read_csv(PATH / "res" / f"_isotherm-{index}-{material}.csv")

        ax.text(0.02, 1.02, f"({i}) {material}", transform=ax.transAxes)

        ax.plot(
            df.iloc[:, 0],
            df.iloc[:, 1],
            color=COLORS[material],
            label="isotherm",
        )

        for i, simulation_file in enumerate(
            glob.glob(str(PATH / "res" / f"_sim-{index}-*"))[::2]
        ):
            label = "C-rate simulations" if i == 0 else ""
            df = pd.read_csv(simulation_file)
            ax.plot(
                df["SOC"],
                df["Potential"],
                color=COLORS[material],
                ls="--",
                alpha=0.25,
                label=label,
            )

        ax.legend()

    for ax in axes:
        ax.set_ylabel("Potential (V)")

    axes[0].set_ylim((3.2, 3.8))
    axes[0].set_xlim((0, 1))

    axes[1].set_ylim((0.07, 1.0))
    axes[1].set_xlim((0, 1))
    axes[1].set_xlabel("SOC")

    fig.tight_layout()
    fig.savefig(PATH / "res" / "simulations.png", dpi=600)


def fit():
    plt.rcParams.update({"font.size": 14})

    fig, ax = plt.subplots()

    for index, material in zip(["06", "24"], ["Graphite", "LFP"]):
        df = pd.read_csv(PATH / "res" / f"_fit-{index}-{material}.csv")

        ax.scatter(
            df["c_rate"],
            df["soc_max"],
            marker=MARKERS[material],
            color=COLORS[material],
            label=f"{material} data",
        )
        ax.plot(
            df["c_rate"],
            df["soc_max_pred"],
            color=COLORS[material],
            label=f"{material} fit",
        )

    ax.set_xlim((1e-2, 40))
    ax.set_xscale("log")
    ax.set_xlabel("C-rate")

    ax.set_ylim((0, 1))
    ax.set_ylabel(r"SOC$_{\max}$")

    ax.legend()

    fig.tight_layout()
    fig.savefig(PATH / "res" / "fit.png", dpi=600)


def map():
    plt.rcParams.update({"font.size": 14})

    fig, ax = plt.subplots()
    ax = None

    particle_sizes = [0.00174, 7.3e-06]
    dcoeffs = [3.5111704723535215e-11, 9.999939445455477e-16]
    k0s = [9.999939445455476e-09, 2.848018622284325e-10]

    C_rates = np.logspace(-2, 2).reshape(-1, 1)
    for material, d, dcoeff, k0 in zip(
        ["Graphite", "LFP"], particle_sizes, dcoeffs, k0s
    ):
        greg = gp.model.GalvanostaticRegressor(d=d)
        greg.fit(C_rates, np.zeros(50))
        greg.dcoeff_, greg.k0_ = dcoeff, k0

        if ax is None:
            ax = greg.plot.render_map(ax=ax, clb_label=r"SOC$_{\max}$")

        ax = greg.plot.in_render_map(
            C_rates, ax=ax, color=COLORS[material], marker=None, label=material
        )

    ax.legend(loc="upper left")
    ax.set_xlim((-4, 1.75))

    fig.tight_layout()
    fig.savefig(PATH / "res" / "map.png", dpi=600)


def _socmax_pred_vs_actual():
    for fit_file in glob.glob(str(PATH / "res" / "_fit-*")):
        df = pd.read_csv(fit_file)

        fig, ax = plt.subplots(figsize=(7, 5))

        ax.scatter(df["c_rate"], df["soc_max"])
        ax.plot(df["c_rate"], df["soc_max_pred"])

        ax.set_title(fit_file)

        ax.set_xscale("log")
        plt.show()


def _isotherms():
    for isotherm_file in glob.glob(str(PATH / "res" / "_isotherm-*")):
        df = pd.read_csv(isotherm_file)

        fig, ax = plt.subplots(figsize=(7, 5))

        ax.plot(df.iloc[:, 0], df.iloc[:, 1])

        ax.set_title(fit_file)

        plt.show()


if __name__ == "__main__":
    dcoeff_pred_vs_db()
    simulations()
    fit()
    map()
    # _socmax_pred_vs_actual()
    # _isotherms()
