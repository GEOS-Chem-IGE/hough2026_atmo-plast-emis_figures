Paper figures
=============

[![DOI](https://zenodo.org/badge/1277829106.svg)](https://zenodo.org/badge/latestdoi/1277829106)

This repository contains code to produce the figures for the paper "Reduced global atmospheric microplastic emissions from size-harmonized observations" (Hough et al., 2026).

The final figures are in [figures/](figures/)


To reproduce
------------

### Create and activate the environment

You will need [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) and [conda-lock](https://conda.github.io/conda-lock/) to create the environment. You may also use [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) instead of micromamba.

```bash
conda-lock install --micromamba -n hough2026_atmo-plast-emis_harmonize
micromamba activate hough2026_atmo-plast-emis_paper
```

### Get the data

The size-harmonized observations are available at https://doi.org/10.5281/zenodo.21069346. Copy the `obs_size-harmonized_*.csv` files (in the `results/` directory) to the [data/](data/) directory.

The constrained simulation outputs are available at https://doi.org/10.5281/zenodo.20922804. Download these files to the [data](data/) directory.

The fraction of each grid cell that is ocean (used to compute net transfer between land and oceans) is stored in the standard GEOS-Chem input file `MERRA2.20150101.CN.2x25.nc4`. You can download it from https://geos-chem.s3-us-west-2.amazonaws.com/GEOS_2x2.5/MERRA2/2015/01/MERRA2.20150101.CN.2x25.nc4.

The [data/](data/) directory tree should look like this:

```
data/
├── MERRA2.20150101.CN.2x25.nc4
├── README.md
├── obs_size-harmonized_concentration.csv
├── obs_size-harmonized_deposition.csv
├── sim_alt_constrained.nc
└── sim_main_constrained.nc
```

Alternatively, you can reproduce these data by running the code at https://doi.org/10.5281/zenodo.21069346.

### Run the notebook

Run [figures.ipynb](notebooks/figures.ipynb) to produce the paper figures.


Contents
--------

### [data/](data/)

Data to produce the figures

### [figures/](figures/)

The figures produced by the notebooks

### [notebooks/](notebooks/)

Notebooks to produce figures

### [utils/](utils/)

Functions used in the notebooks


References
----------

Hough, I., Angot, H., Price, R., Dobiasova, N., Segur, T., Jahangir, E., Zhang, Y., Voisin, D., Sonke, J.E., & Thomas, J.L. (2026) Reduced global atmospheric microplastic emissions from size-harmonized observations. TODO PAPER DOI
