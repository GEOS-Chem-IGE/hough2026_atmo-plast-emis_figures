Data
====

This directory exists to hold the observations and constrained simulation outputs needed to produce the figures. You can download these data from https://doi.org/10.5281/zenodo.20922804 or recreate them by running the code at https://doi.org/10.5281/zenodo.21069346.


Contents
--------

`MERRA2.20150101.CN.2x25.nc4`: standard GEOS-Chem input file containing the `FROCEAN` constant (fraction of each model grid cell that is occupied by ocean). Downloaded from https://geos-chem.s3-us-west-2.amazonaws.com/GEOS_2x2.5/MERRA2/2015/01/MERRA2.20150101.CN.2x25.nc4.

`obs_revised_*.csv`: revised observations of atmospheric microplastic conentration and deposition. The original observations were collected from the literature by Fu et al. (2023). We revised the observations adding study DOI and observed particle size range and ensuring lat/lon and microplastic particle counts correspond to the study-reported values. We then recomputed microplastic mass from the updated particle counts using @Fu2023's assumed fixed microplastic particle mass of 57 ng/particle over land and 100 ng/particle over oceans.

`obs_size-harmonzied_*.csv`: size-harmonized atmospheric microplastic concentration and deposition observations.

`sim_*_constrained.nc`: constrained outputs of the *main* and *alternate* simulations.


References
----------

Fu, Y., Pang, Q., Ga, S. L. Z., Wu, P., Wang, Y., Mao, M., Yuan, Z., Xu, X., Liu, K., Wang, X., Li, D., & Zhang, Y. (2023). Modeling atmospheric microplastic cycle by GEOS-Chem: An optimized estimation by a global dataset suggests likely 50 times lower ocean emissions. *One Earth*, *6*(6), 705–714. https://doi.org/10.1016/j.oneear.2023.05.012
