#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Full regression-based Waveform Estimation (rERP) analysis of:
#
# Delogu, F., Brouwer, H., and Crocker, M. W. (2021). When components
# collide: Spatiotemporal overlap of the N400 and P600 in language
# comprehension. Brain Research. doi: 10.1016/j.brainres.2021.147514
#
# 10/05/21: Harm Brouwer <me@hbrouwer.eu>

import rerps.models
import rerps.plots

import numpy as np
import pandas as pd

def generate():
    obs_data = rerps.models.DataSet(
        filename    = "data/dbc_data.csv",
        descriptors = ["Subject", "Timestamp", "Condition", "ItemNum"],
        electrodes  = ["F3" , "Fz", "F4", "FC5", "FC1", "FC2", "FC6", "C3",  "Cz", "C4",
                       "CP5", "CP1", "CP2", "CP6", "P3","Pz", "P4", "O1",  "Oz", "O2"],
        predictors  = ["Plaus", "Assoc", "Cloze"])

    obs_data.rename_descriptor_level("Condition", "baseline",    "Related-Plausible")
    obs_data.rename_descriptor_level("Condition", "plausible",   "Unrelated-Plausible")
    obs_data.rename_descriptor_level("Condition", "implausible", "Unrelated-Implausible")

    obs_data.rename_predictor("Plaus", "plausibility")
    obs_data.rename_predictor("Assoc", "association")
    obs_data.rename_predictor("Cloze", "cloze")

    obs_data.invert_predictor("plausibility", 7.0)
    obs_data.invert_predictor("association",  7.0)
    obs_data.invert_predictor("cloze",        1.0)

    obs_data.zscore_predictor("plausibility")
    obs_data.zscore_predictor("association")
    obs_data.zscore_predictor("cloze")

    electrode_grid = [["F3" , "Fz", "F4" ],
                      ["FC1", "",   "FC2"],
                      ["C3",  "Cz", "C4" ],
                      ["CP1", "",   "CP2"],
                      ["P3",  "Pz", "P4" ],
                      ["O1",  "Oz", "O2" ]]

    electrode_grid_subset = [["", "Pz", ""],
                             ["", "",   ""]]

    group_order = ["Related-Plausible", "Unrelated-Plausible", "Unrelated-Implausible"]

        ####################
        #### potentials ####
        ####################
    
    print("\n[ figures/dbc_potentials.pdf ]\n")
    obs_data_summary = rerps.models.DataSummary(obs_data, ["Condition", "Subject", "Timestamp"])
    obs_data_summary = rerps.models.DataSummary(obs_data_summary, ["Condition", "Timestamp"])
    colors = ["black", "red", "blue"]
    fig, ax = rerps.plots.plot_voltages_grid(obs_data_summary, "Timestamp", electrode_grid,
            ["Oz"], "Condition", group_order, title="Event-Related Potentials", colors=colors)
    fig.set_size_inches(35, 30)
    fig.savefig("figures/dbc_potentials.pdf", bbox_inches='tight')
    fig, ax = rerps.plots.plot_voltages_grid(obs_data_summary, "Timestamp", electrode_grid_subset,
            ["Pz"], "Condition", group_order, title="Event-Related Potentials", colors=colors)
    fig.set_size_inches(25, 10)
    fig.savefig("figures/dbc_potentials_Pz.pdf", bbox_inches='tight')
   
    print("\n[ stats/dbc_potentials_100-300.csv ]\n")
    time_window_averages(obs_data, 100, 300 ).to_csv("stats/dbc_potentials_100-300.csv",  index=False)
    print("\n[ stats/dbc_potentials_300-500.csv ]\n")
    time_window_averages(obs_data, 300, 500 ).to_csv("stats/dbc_potentials_300-500.csv",  index=False)
    print("\n[ stats/dbc_potentials_600-1000.csv ]\n")
    time_window_averages(obs_data, 600, 1000).to_csv("stats/dbc_potentials_600-1000.csv", index=False)

        ####################################
        #### plausibility + association ####
        ####################################

    print("\n[ figures/dbc_plaus+assoc_est.pdf ]\n")
    models = rerps.models.regress(obs_data, ["Subject", "Timestamp"], ["plausibility", "association"])
    est_data = rerps.models.estimate(obs_data, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["black", "red", "blue"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", electrode_grid,
            ["Oz"], "Condition", group_order, title="regression-based Event-Related Potentials", colors=colors)
    fig.set_size_inches(35, 30)
    fig.savefig("figures/dbc_plaus+assoc_est.pdf", bbox_inches='tight')

    print("\n[ figures/dbc_plaus+assoc_res.pdf ]\n")
    res_data = rerps.models.residuals(obs_data, est_data)
    res_data_summary = rerps.models.DataSummary(res_data, ["Condition", "Subject", "Timestamp"])
    res_data_summary = rerps.models.DataSummary(res_data_summary, ["Condition", "Timestamp"])
    colors = ["black", "red", "blue"]
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", electrode_grid,
            ["Oz"], "Condition", group_order, title="Residuals", colors=colors, ymin=2, ymax=-2)
    fig.set_size_inches(35, 30)
    fig.savefig("figures/dbc_plaus+assoc_res.pdf", bbox_inches='tight')
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", electrode_grid_subset,
            ["Pz"], "Condition", group_order, title="Residuals", colors=colors, ymin=2, ymax=-2)
    fig.set_size_inches(25, 10)
    fig.savefig("figures/dbc_plaus+assoc_res_Pz.pdf", bbox_inches='tight')

    print("\n[ figures/dbc_plaus+assoc_coef.pdf ]\n")
    models_summary = rerps.models.ModelSummary(models, ["Timestamp"])
    colors = ["#d62728", "#9467bd", "#8c564b"]
    fig, ax = rerps.plots.plot_coefficients_grid(models_summary, "Timestamp", electrode_grid,
            ["Oz"], anchor=True, title="Coefficients", colors=colors)
    fig.set_size_inches(35, 30)
    fig.savefig("figures/dbc_plaus+assoc_coef.pdf", bbox_inches='tight')
    fig, ax = rerps.plots.plot_coefficients_grid(models_summary, "Timestamp", electrode_grid_subset,
            ["Pz"], anchor=True, title="Coefficients", colors=colors)
    fig.set_size_inches(25, 10)
    fig.savefig("figures/dbc_plaus+assoc_coef_Pz.pdf", bbox_inches='tight')

    print("\n[ figures/dbc_plaus0+assoc_est.pdf ]\n")
    obs_data0 = obs_data.copy()
    obs_data0.array[:,obs_data0.predictors["plausibility"]] = 0
    est_data = rerps.models.estimate(obs_data0, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["black", "red", "blue"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", electrode_grid,
            ["Oz"], "Condition", group_order, title="regression-based Event-Related Potentials", colors=colors)
    fig.set_size_inches(35, 30)
    fig.savefig("figures/dbc_plaus0+assoc_est.pdf", bbox_inches='tight')
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", electrode_grid_subset,
            ["Pz"], "Condition", group_order, title="rERPs: Effect of Association", colors=colors)
    fig.set_size_inches(25, 10)
    fig.savefig("figures/dbc_plaus0+assoc_est_Pz.pdf", bbox_inches='tight')

    print("\n[ figures/dbc_plaus+assoc0_est.pdf ]\n")
    obs_data0 = obs_data.copy()
    obs_data0.array[:,obs_data0.predictors["association"]] = 0
    est_data = rerps.models.estimate(obs_data0, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["black", "red", "blue"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", electrode_grid,
            ["Oz"], "Condition", group_order, title="regression-based Event-Related Potentials", colors=colors)
    fig.set_size_inches(35, 30)
    fig.savefig("figures/dbc_plaus+assoc0_est.pdf", bbox_inches='tight')
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", electrode_grid_subset,
            ["Pz"], "Condition", group_order, title="rERPs: Effect of Plausibility", colors=colors)
    fig.set_size_inches(25, 10)
    fig.savefig("figures/dbc_plaus+assoc0_est_Pz.pdf", bbox_inches='tight')

        ##############################
        #### plausibility + cloze ####
        ##############################

    print("\n[ figures/dbc_plaus+cloze_est.pdf ]\n")
    models = rerps.models.regress(obs_data, ["Subject", "Timestamp"], ["plausibility", "cloze"])
    est_data = rerps.models.estimate(obs_data, models)
    est_data_summary = rerps.models.DataSummary(est_data, ["Condition", "Subject", "Timestamp"])
    est_data_summary = rerps.models.DataSummary(est_data_summary, ["Condition", "Timestamp"])
    colors = ["black", "red", "blue"]
    fig, ax = rerps.plots.plot_voltages_grid(est_data_summary, "Timestamp", electrode_grid,
            ["Oz"], "Condition", group_order, title="regression-based Event-Related Potentials", colors=colors)
    fig.set_size_inches(35, 30)
    fig.savefig("figures/dbc_plaus+cloze_est.pdf", bbox_inches='tight')

    print("\n[ figures/dbc_plaus+cloze_res.pdf ]\n")
    res_data = rerps.models.residuals(obs_data, est_data)
    res_data_summary = rerps.models.DataSummary(res_data, ["Condition", "Subject", "Timestamp"])
    res_data_summary = rerps.models.DataSummary(res_data_summary, ["Condition", "Timestamp"])
    colors = ["black", "red", "blue"]
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", electrode_grid,
            ["Oz"], "Condition", group_order, title="Residuals", colors=colors, ymin=2, ymax=-2)
    fig.set_size_inches(35, 30)
    fig.savefig("figures/dbc_plaus+cloze_res.pdf", bbox_inches='tight')
    fig, ax = rerps.plots.plot_voltages_grid(res_data_summary, "Timestamp", electrode_grid_subset,
            ["Pz"], "Condition", group_order, title="Residuals", colors=colors, ymin=2, ymax=-2)
    fig.set_size_inches(25, 10)
    fig.savefig("figures/dbc_plaus+cloze_res_Pz.pdf", bbox_inches='tight')

    print("\n[ figures/dbc_plaus+cloze_coef.pdf ]\n")
    models_summary = rerps.models.ModelSummary(models, ["Timestamp"])
    colors = ["#d62728", "#9467bd", "#8c564b"]
    fig, ax = rerps.plots.plot_coefficients_grid(models_summary, "Timestamp", electrode_grid,
            ["Oz"], anchor=True, title="Coefficients", colors=colors)
    fig.set_size_inches(35, 30)
    fig.savefig("figures/dbc_plaus+cloze_coef.pdf", bbox_inches='tight')
    fig, ax = rerps.plots.plot_coefficients_grid(models_summary, "Timestamp", electrode_grid_subset,
            ["Pz"], anchor=True, title="Coefficients", colors=colors)
    fig.set_size_inches(25, 10)
    fig.savefig("figures/dbc_plaus+cloze_coef_Pz.pdf", bbox_inches='tight')

###########################################################################
###########################################################################

def time_window_averages(ds, start, end):
    ts_idx = ds.descriptors["Timestamp"]
    sds = ds.copy()
    sds.array = sds.array[(sds.array[:,ts_idx] >= start) & (sds.array[:,ts_idx] < end),:]
    sds_summary = rerps.models.DataSummary(sds, ["Condition", "Subject"])

    nrows = sds_summary.means.shape[0] * len(sds_summary.electrodes)
    sds_lf = np.empty((nrows, 4), dtype=object)

    sds_idx = 0
    for idx in range(0, sds_summary.means.shape[0]):
        c = sds_summary.means[idx, sds_summary.descriptors["Condition"]]
        s = sds_summary.means[idx, sds_summary.descriptors["Subject"]]
        for e, i in sds_summary.electrodes.items():
            sds_lf[sds_idx,:] = [c, s, e, sds_summary.means[idx,i]]
            sds_idx = sds_idx + 1

    return pd.DataFrame(sds_lf, columns=["cond", "subject", "ch", "eeg"])

###########################################################################
###########################################################################

if __name__ == "__main__":
    generate()
