# About

This implements the regression-based waveform estimation (rERP) analysis detailed in:

[Delogu, F., Brouwer, H., and Crocker, M. W. (2021). When components collide: Spatiotemporal overlap of the N400 and P600 in language comprehension. *Brain Research*. doi: 10.1016/j.brainres.2021.147514](https://www.sciencedirect.com/science/article/pii/S0006899321003711)

# Getting started

Clone this repository, download the data files (see Releases) and decompress them in the repository folder. 

# Requirements

To run the analysis, you need:

* A recent version of Python 3, with recent versions of:
  * NumPy
  * pandas
  * SciPy
  * Matplotlib
* GNU Make (optional)

# Usage

To build the rERP analysis, including all graphs and time-window averages:

```
$ make analysis
```

To undo everything:

```
$ make clean
```
