Data
====

This directory exists to hold the observations and constrained simulation outputs needed to produce the figures. You can download the archived data from https://doi.org/10.5281/zenodo.22946011.


Contents
--------

`sensitivity/`: constrained outputs of the sensitivity analysis simulations.

- `obs_evangelou2025-size-harmonized_obs-{10|20|50}-{200|500|1000}.csv`: revised observational dataset of Evangelou et al. (2026) size-harmonized assuming varying observed size ranges.
- `obs_fu2023-size-harmonized_alpha{+|-}1sd.csv`: revised observational dataset of Fu et al. (2023) size harmonized using an alternate PSD slope (plus/minus one standard deviation).
- `sim_evangelou2025-size-harmonized_obs-{10|20|50}-{200|500|1000}_constrained.nc`: outputs of the *main* simulation constrained by the Evangelou et al. (2026) observations (`obs_evangelou2025-size-harmonized_obs-{10|20|50}-{200|500|1000}.csv`)
- `sim_alpha{+|-}1sd_constrained.nc`: outputs of the *main* simulation constrained by the alternate PSD slope observations (`obs_fu2023-size-harmonized_alpha{+|-}1sd.csv`)

`MERRA2.20150101.CN.2x25.nc4`: standard GEOS-Chem input file containing the `FROCEAN` constant (fraction of each model grid cell that is occupied by ocean). Downloaded from https://geos-chem.s3-us-west-2.amazonaws.com/GEOS_2x2.5/MERRA2/2015/01/MERRA2.20150101.CN.2x25.nc4.

`obs_fu2023-revised.csv`: observational dataset of Fu et al. (2023), revised to ensure lat/lon and microplastic particle counts (`particle/m3` or `particle/m2/d`) correspond to the study-reported values. Microplastic mass (`ug/m3` or `t/km2/yr`) was recomputed from the updated particle counts assuming a fixed microplastic particle mass of 57 ng/particle over land and 100 ng/particle over oceans.

`obs_fu2023-size-harmonzied.csv`: revised observational dataset of Fu et al. (2023) size-harmonized to the 0.1-100 µm particle size range. All observations were assumed to have a power law particle number size distribution with $\alpha$ = -2.7 (i.e. the log-log slope of the particle number size distribution is -2.7). Mass was computed assuming ellipsoidal particles with length = size, width = 0.68 length, height = 0.4 width, and density 1 g/cm3.

`sim_{main|alt}_constrained.nc`: constrained outputs of the *main* and *alternate* simulations obtained by multiplying the postprocessed raw outputs by the optimized scaling factors.


References
----------

Evangelou, I., Bucci, S., & Stohl, A. (2026). Atmospheric microplastic emissions from land and ocean. *Nature*, *649*(8099), 1186–1189. https://doi.org/10.1038/s41586-025-09998-6

Fu, Y., Pang, Q., Ga, S. L. Z., Wu, P., Wang, Y., Mao, M., Yuan, Z., Xu, X., Liu, K., Wang, X., Li, D., & Zhang, Y. (2023). Modeling atmospheric microplastic cycle by GEOS-Chem: An optimized estimation by a global dataset suggests likely 50 times lower ocean emissions. *One Earth*, *6*(6), 705–714. https://doi.org/10.1016/j.oneear.2023.05.012
