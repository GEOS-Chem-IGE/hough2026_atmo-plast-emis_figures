"""Helper functions for loading and transforming data"""

import os

# isort: off
import xarray as xr
import pint_xarray
import cf_xarray.units
# isort: on

import pandas as pd

DATA_DIR = "data"  # processed data and results of previous analyses
FIGURES_DIR = "figures"


def load_observations(
    filename: str, data_dir: str = DATA_DIR, label: str | None = None
) -> xr.Dataset:
    """Load processed observations as an xr.Dataset"""

    # Parse label from filename
    file_label = filename.removeprefix("obs_").removesuffix(".csv").replace("_", "-")
    if not label:
        label = file_label

    # Load data
    path = os.path.join(data_dir, filename)
    obs = pd.read_csv(path)

    # Exclude observations with no microplastics
    obs = obs.loc[obs["mass"].gt(0), :].reset_index(drop=True)

    # Check units
    units = {}
    for col in ["number", "mass"]:
        units[col] = {}
        for measure in ["concentration", "deposition"]:
            obs_units = (
                obs.loc[obs["measure"].eq(measure), f"{col}_units"].dropna().unique()
            )
            if len(obs_units) > 1:
                raise ValueError(
                    f"All {measure} observations must have same {col} units; got {obs_units}"
                )
            units[col][measure] = obs_units[0]
    size_units = obs["size_units"].dropna().unique()
    if len(size_units) > 1:
        raise ValueError(f"All observations must have same size units; got {size_units}")
    size_units = size_units[0]

    # Convert to xr.Dataset
    # fmt: off
    cols = [
        "author", "year", "doi", "measure", "lat", "lon", "size_min", "size_max",
        "number", "mass", "shape", "area"
    ]
    # fmt: on
    cols = [x for x in cols if x in obs.columns]
    obs = obs[cols].to_xarray().set_coords(["lat", "lon"])
    for measure in ["concentration", "deposition"]:
        mask = obs["measure"] == measure
        for variable in ["number", "mass"]:
            varname = f"{variable}_{measure}"
            obs[varname] = xr.where(mask, obs[variable], None)
            obs[varname].attrs.update(
                long_name=f"{variable.title()} {measure} of microplastics",
                units=units[variable][measure],
            )
    obs = obs.drop_vars(["measure", "number", "mass"])

    # Set attributes
    obs["lat"].attrs.update(standard_name="latitude", units="degrees_north", axis="Y")
    obs["lon"].attrs.update(standard_name="longitude", units="degrees_east", axis="X")
    obs["size_min"].attrs.update(long_name="Aerodynamic diameter", units=size_units)
    obs["size_max"].attrs.update(long_name="Aerodynamic diameter", units=size_units)
    obs.attrs["description"] = "Atmospheric microplastic observations"
    obs.attrs["label"] = label

    return obs


def spatial_integrate(
    dataset: xr.Dataset,
    varname: str,
    units: str | None = None,
    sum_dims: list[str] | str | None = None,
) -> xr.DataArray:
    """Multiply a variable by cell area and sum over all grid cells

    Args:
        data: Dataset with variable to integrate
        varname: Name of variable to integrate
        units: Optional units for output
        sum_dims: Optional dimensions to sum over in addition to [lat, lon]
    """

    # Check inputs
    varnames = [
        "emission",
        "concentration",
        "total_deposition",
        "dry_deposition",
        "wet_loss",
    ]
    if varname not in varnames:
        raise ValueError(f"Unrecognized varname: '{varname}'. Must be one of {varnames}")
    if varname == "concentration":
        if "air_volume" not in dataset.data_vars:
            raise ValueError(
                "data must have variable 'air_volume' to compute atmospheric burden"
            )
    elif "area" not in dataset.data_vars:
        raise ValueError(f"data must have variable 'area' to compute global {varname}")

    # Set target units
    if units is None:
        units = "Gg" if varname == "concentration" else "Gg/year"

    # Set dimensions over which to sum
    if sum_dims is None:
        sum_dims = []
    elif isinstance(sum_dims, str):
        sum_dims = [sum_dims]
    sum_dims = sum_dims + ["lat", "lon"]
    if varname == "concentration":
        sum_dims = sum_dims + ["lev"]

    # Multiply by cell area and sum
    if varname == "concentration":
        integrated = (
            (dataset[varname].pint.quantify() * dataset["air_volume"].pint.quantify())
            .sum(dim=sum_dims)
            .rename("burden")
        )
    else:
        integrated = (
            (dataset[varname].pint.quantify() * dataset["area"].pint.quantify())
            .sum(dim=sum_dims)
            .rename(varname)
        )

    # Convert units
    integrated = integrated.pint.to(units).pint.dequantify("cf")

    # Assign dataset label, if any
    label = dataset.attrs.get("label")
    if label:
        integrated.attrs["label"] = label

    return integrated
