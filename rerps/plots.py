#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2020 Harm Brouwer <me@hbrouwer.eu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ---- Last modified: March 2021, Harm Brouwer ----

import rerps.models as models

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'figure.max_open_warning': 0})

"""regression-based ERP estimation.
    
Minimal implementation of regression-based ERP (rERP) waveform estimation,
as proposed in:

Smith, N.J., Kutas, M., Regression-based estimation of ERP waveforms: I. The
    rERP framework, Psychophysiology, 2015, Vol. 52, pp. 157-168

Smith, N.J., Kutas, M., Regression-based estimation of ERP waveforms: II.
    Non-linear effects, overlap correction, and practical considerations,
    Psychophysiology, 2015, Vol. 52, pp. 169-181

This module implements plotting of (r)ERP waveforms and model coefficients.

"""

def plot_voltages(dsm, x, y, groupby, group_order=None, title=None, title_fontsize=14, legend=True, legend_fontsize=12, ax=None, colors=None, ymin=None, ymax=None):
    """Plots voltages for a single electrode.

    Args:
        dsm (:obj:`DataSummary`):
            Summary of an Event-Related brain Potentials data set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        y (:obj:`str`):
            name of electrode to be plotted.
        groupby (:obj:`str`):
            name of the descriptor column that determines the grouping
            (typically 'condition').
        group_order (:obj:`list` of :obj:`str`):
            custom order for grouping descriptor
        title (:obj:`str`):
            title of the graph
        title_fontsize (:obj:`int`):
            font size of the title
        legend (:obj:`bool`):
            flags whether a legend should be added.
        legend_fontsize (:obj:`int`):
            font size of the legend
        ax (:obj:`Axes`):
            axes.Axes object to plot to.
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting
        ymin (:obj:`float`):
            minimum of y axis
        ymax (:obj:`float`):
            maximum of y axis

    Returns:
        (:obj:`Figure`, optional): Figure
        (:obj:`Axes`): axes.Axes object.

    """
    newfig = False
    if (ax == None):
        newfig = True
        fig, ax = plt.subplots()
        ax.invert_yaxis()

    if (colors):
        ax.set_prop_cycle(color=colors)

    groups = np.unique(dsm.means[:,dsm.descriptors[groupby]])
    if (set(group_order) == set(groups)):
        groups = group_order
    for g in groups:
        # means
        x_vals = dsm.means[dsm.means[:,
            dsm.descriptors[groupby]] == g,
            dsm.descriptors[x]]
        x_vals = x_vals.astype(float)
        y_vals = dsm.means[dsm.means[:,
            dsm.descriptors[groupby]] == g,
            dsm.electrodes[y]]
        y_vals = y_vals.astype(float)
        ax.plot(x_vals, y_vals, label=g, linewidth=3)
        # CIs
        y_sems = dsm.sems[dsm.sems[:,
            dsm.descriptors[groupby]] == g,
            dsm.electrodes[y]]
        y_sems = y_sems.astype(float)
        y_lvals = y_vals - 2 * y_sems
        y_uvals = y_vals + 2 * y_sems
        ax.fill_between(x_vals, y_lvals, y_uvals, alpha=.2)

    ax.grid()
    ax.axvspan(300,500,  color="grey", alpha=0.2)
    ax.axvspan(600,1000, color="grey", alpha=0.2)
    ax.axhline(y=0, color="black")
    ax.axvline(x=0, color="black")
    
    ax.tick_params(axis="both", which="major", labelsize=12)
    ax.tick_params(axis="both", which="minor", labelsize=12)

    ax.xaxis.set_tick_params(labelbottom=True)
    ax.yaxis.set_tick_params(labelleft=True)

    if (ymin and ymax):
        ax.set_ylim(ymin, ymax)

    if (legend):
        ax.legend(loc = "lower left", fontsize=legend_fontsize)
    if (title):
        ax.set_title(title, fontsize=title_fontsize)

    if (newfig):
        return fig, ax
    else:
        return ax

def plot_voltages_grid(dsm, x, electrode_grid, legend_electrodes, groupby, group_order=None, title=None, colors=None, ymin=None, ymax=None):
    """Plots voltages for a grid of electrodes.

    Args:
        dsm (:obj:`DataSet`):
            Summary of an Event-Related brain Potentials data set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        electrode_grid(:obj:`list` of :obj:`list` of :obj:`str`):
            grid of electrodes to be plotted.
        legend_electrodes (:obj:`list` of :obj:`str`):
            names of electrodes to which a legend should be added.
        groupby (:obj:`str`):
            name of the descriptor column that determines the grouping
            (typically 'condition').
        group_order (:obj:`list` of :obj:`str`):
            custom order for grouping descriptor
        title (:obj:`str`):
            global title of the graph
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting
        ymin (:obj:`float`):
            minimum of y axis
        ymax (:obj:`float`):
            maximum of y axis

    Returns:
        (:obj:`Figure`): Figure
        (:obj:`Axes`): axes.Axes object.

    """
    fig, axes = plt.subplots(len(electrode_grid), len(electrode_grid[0]), sharey=True)

    suptitle_fontsize = 42
    title_fontsize    = 28
    legend_fontsize   = 19
    es = set([e for r in electrode_grid for e in r])
    es.remove('')
    if (len(es) == 1):
        suptitle_fontsize = 16
        title_fontsize    = 14
        legend_fontsize   = 12
    
    axes[0,0].invert_yaxis()
    for r, electrodes in enumerate(electrode_grid):
        for c, y in enumerate(electrodes):
            if (y == ''):
                axes[r,c].set_visible(False)
            else:
                legend = False
                if (y in legend_electrodes):
                    legend = True;
                plot_voltages(dsm, x, y, groupby, group_order, title=y, title_fontsize=title_fontsize, legend=legend, legend_fontsize=legend_fontsize, ax=axes[r,c], colors=colors, ymin=ymin, ymax=ymax)

    if (title):
        fig.suptitle(title, fontsize=suptitle_fontsize, x=.5, y=.95)

    return fig, axes

def plot_coefficients(msm, x, y, anchor=True, title=None, title_fontsize=14, legend=True, legend_fontsize=12, ax=None, colors=None, ymin=None, ymax=None):
    """Plots coefficients for a single electrode.
    
    Args:
        msm (:obj:`DataSet`):
            Summary of a Linear regression coefficients set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        y (:obj:`str`):
            name of electrode to be plotted.
        anchor (:obj:`bool`):
            flags whether slopes should be anchored to the intercept.
        title (:obj:`str`):
            global title of the graph
        title_fontsize (:obj:`int`):
            font size of the title
        legend (:obj:`bool`):
            flags whether a legend should be added.
        legend_fontsize (:obj:`int`):
            font size of the legend
        ax (:obj:`Axes`):
            axes.Axes object to plot to.
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting
        ymin (:obj:`float`):
            minimum of y axis
        ymax (:obj:`float`):
            maximum of y axis

    Returns:
        (:obj:`Figure`, optional): Figure
        (:obj:`Axes`): axes.Axes object.
    
    """
    newfig = False
    if (ax == None):
        newfig = True
        fig, ax = plt.subplots()
        ax.invert_yaxis()

    if (colors):
        ax.set_prop_cycle(color=colors)
    
    for i, p in enumerate(msm.predictors):
        # means
        x_vals = msm.means[:,msm.descriptors[x]]
        x_vals = x_vals.astype(float)
        y_vals = msm.means[:,msm.coefficients[(y,p)]]
        y_vals = y_vals.astype(float)
        l = p
        if (anchor and i > 0):
            i_vals = msm.means[:,msm.coefficients[(y,msm.predictors[0])]]
            i_vals = i_vals.astype(float)
            y_vals = y_vals + i_vals
            l = msm.predictors[0] + " + " + p
        ax.plot(x_vals, y_vals, label=l, linewidth=3)
        # CIs
        y_sems = msm.sems[:,msm.coefficients[(y,p)]]
        y_sems = y_sems.astype(float)
        y_lvals = y_vals - 2 * y_sems
        y_uvals = y_vals + 2 * y_sems
        ax.fill_between(x_vals, y_lvals, y_uvals, alpha=.2)

    ax.grid()
    ax.axvspan(300,500,  color="grey", alpha=0.2)
    ax.axvspan(600,1000, color="grey", alpha=0.2)
    ax.axhline(y=0, color="black")
    ax.axvline(x=0, color="black")
    
    ax.tick_params(axis="both", which="major", labelsize=12)
    ax.tick_params(axis="both", which="minor", labelsize=12)
    
    ax.xaxis.set_tick_params(labelbottom=True)
    ax.yaxis.set_tick_params(labelleft=True)
    
    if (ymin and ymax):
        ax.set_ylim(ymin, ymax)
    
    if (legend):
        ax.legend(loc = "lower left", fontsize=legend_fontsize)
    if (title):
        ax.set_title(title, fontsize=title_fontsize)

    if (newfig):
        return fig, ax
    else:
        return ax

def plot_coefficients_grid(msm, x,electrode_grid, legend_electrodes, anchor=True, title=None, colors=None, ymin=None, ymax=None):
    """Plots coefficients for a grid of electrodes.

    Args:
        msm (:obj:`DataSet`):
            Summary of a Linear regression coefficients set.
        x (:obj:`str`):
            name of the descriptor column that determines the x-axis
            (typically 'time').
        electrode_grid(:obj:`list` of :obj:`list` of :obj:`str`):
            grid of electrodes to be plotted.
        legend_electrodes (:obj:`list` of :obj:`str`):
            names of electrodes to which a legend should be added.
        anchor (:obj:`bool`):
            flags whether slopes should be anchored to the intercept.
        title (:obj:`str`):
            global title of the graph
        colors (:obj:`list` of :obj:`str`):
            list of colors to use for plotting
        ymin (:obj:`float`):
            minimum of y axis
        ymax (:obj:`float`):
            maximum of y axis

    Returns:
        (:obj:`Figure`): Figure
        (:obj:`Axes`): axes.Axes object.

    """
    fig, axes = plt.subplots(len(electrode_grid), len(electrode_grid[0]), sharey=True)

    suptitle_fontsize = 42
    title_fontsize    = 28
    legend_fontsize   = 19
    es = set([e for r in electrode_grid for e in r])
    es.remove('')
    if (len(es) == 1):
        suptitle_fontsize = 16
        title_fontsize    = 14
        legend_fontsize   = 12

    axes[0,0].invert_yaxis()
    for r, electrodes in enumerate(electrode_grid):
        for c, y in enumerate(electrodes):
            if (y == ''):
                axes[r,c].set_visible(False)
            else:
                legend = False
                if (y in legend_electrodes):
                    legend = True;
                plot_coefficients(msm, x, y, anchor=anchor, title=y, title_fontsize=title_fontsize, legend=legend, legend_fontsize=legend_fontsize, ax=axes[r,c], colors=colors, ymin=ymin, ymax=ymax)

    if (title):
        fig.suptitle(title, fontsize=suptitle_fontsize, x=.5, y=.95)
   
    return fig, axes
