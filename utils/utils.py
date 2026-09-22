"""General helper functions"""

import os
import re

# isort: off
import xarray as xr
import pint_xarray
import cf_xarray.units
# isort: on

import numpy as np
import pandas as pd
from matplotlib import colors
from numpy.typing import ArrayLike
from pint import Quantity
from pint.errors import DimensionalityError
from pint_xarray import unit_registry as ureg

# Density of microplastic aerosols
PLASTIC_DENSITY = 1 * ureg("g/cm3")

# Shape factors for atmospheric microplastics
# Multiplier to compute volume from cube of particle size
PLASTIC_SHAPE_FACTORS = {
    # Ellipse volume = pi / 6 * length * width * height
    "fragments": np.pi / 6 * 0.68 * (0.4 * 0.68),  # l = 1; h = 0.68 l; w = 0.4 h
}

# Colormap for plots
WhBlYlRd = colors.ListedColormap(
    np.genfromtxt(os.path.join(os.path.dirname(__file__), "WhBlYlRd.txt")) / 255,
    name="WhBlYlRd",
)


def format_units_mpl(x: str) -> str:
    """Format units for display on matplotlib plots"""

    return re.sub(r"(-?\d+)", r"$^{\1}$", x)


def load_observations(path: str, label: str | None = None) -> xr.Dataset:
    """Load processed observations as an xr.Dataset"""

    # Parse label from filename
    filename = os.path.basename(path)
    file_label = filename.removeprefix("obs_").removesuffix(".csv").replace("_", "-")
    if not label:
        label = file_label

    # Load data
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


def mass_to_particles(
    mass: xr.DataArray,
    shape_factor: float = PLASTIC_SHAPE_FACTORS["fragments"],
    density: Quantity = PLASTIC_DENSITY,
) -> xr.DataArray:
    """Convert mass to number of paticles

    Args:
        mass: Mass of particles. Must have coordinate "size" that stores volume-weighted
            mean particle size for each size bin.
        shape_factor: Multiplier to compute volume from cube of particle size (default:
            0.0968 i.e. fragments)
        density: Particle density (default: 1 g/cm3)

    Returns:
        Number of particles in each size bin
    """

    # Determine final units
    mass = mass.pint.quantify()
    for unit_str, unit_exp in mass.pint.units._units.items():
        if unit_exp > 0:
            base_unit = ureg(unit_str)
            if base_unit.dimensionality == "[mass]":
                mass_unit = base_unit.units
                break
    else:
        raise ValueError(f"No mass dimension found in unit {mass.pint.units}")
    units = ureg("particle").units * (mass.pint.units / mass_unit)

    volume = shape_factor * xr.DataArray(mass["size"]).pint.quantify() ** 3
    mass_per_particle = volume * density * ureg("1/particle")
    with xr.set_options(keep_attrs=True):
        particles = (mass * (1 / mass_per_particle)).pint.to(units)
        particles = particles.pint.dequantify().rename(mass.name)

    return particles


def particles_to_mass(
    particles: xr.DataArray,
    shape_factor: float = PLASTIC_SHAPE_FACTORS["fragments"],
    density: Quantity = PLASTIC_DENSITY,
) -> xr.DataArray:
    """Convert number of particles to mass

    Args:
        particles: Number of particles. Must have coordinate "size" that stores
            volume-weighted mean particle size for each size bin.
        shape_factor: Multiplier to compute volume from cube of particle size (default:
            0.0968 i.e. fragments)
        density: Particle density (default: 1 g/cm3)

    Returns:
        Mass of particles in each size bin
    """

    # Determine final units
    particles = particles.pint.quantify()
    for unit_str, unit_exp in particles.pint.units._units.items():
        if unit_exp > 0:
            base_unit = ureg(unit_str)
            if base_unit.dimensionality == "[substance]":
                particle_unit = base_unit.units
                break
    else:
        raise ValueError(f"No particles dimension found in unit {particles.pint.units}")
    units = ureg("Gg").units * (particles.pint.units / particle_unit)

    volume = shape_factor * xr.DataArray(particles["size"]).pint.quantify() ** 3
    mass_per_particle = volume * density * ureg("1/particle")
    with xr.set_options(keep_attrs=True):
        mass = (particles * mass_per_particle).pint.to(units)
        mass = mass.pint.dequantify().rename(particles.name)

    return mass


def powerlaw_compute_mass(
    xmin: Quantity,
    xmax: Quantity,
    alpha: float | ArrayLike,
    c: Quantity,
    shape_factor: float | ArrayLike,
    density: Quantity,
) -> Quantity:
    """
    Compute mass in size range assuming power law particle size distribution

    Power law mass size distribution:
        M(x) = rho * k * C * x^(3 - alpha)

    Args:
        xmin, xmax: Size range bounds
        alpha: Power law parameter alpha, the exponent (must be > 1)
        c: Power law parameter C
        shape_factor: Multiplier to compute volume from cube of particle size
        density: Particle density

    All arguments must have size 1 or n.

    Returns:
        Mass of particles in size range(s) [xmin, xmax]

    Derivation (rho = density; k = shape factor):
                 m(x) = rho * k * x^3
                 n(x) = C * x^-alpha
        M(xmin, xmax) = Integral[m(x) * n(x)] dx
                      = Integral[rho * k * C * x^(3 - alpha)] dx
                      = rho * k * C / (4 - alpha) * [xmax^(4 - alpha) - xmin^(4 - alpha)]
    """

    alpha = np.asarray(alpha).astype(float)  # numpy disallows negative integer powers
    if np.any(alpha <= 1):
        raise ValueError(f"alpha must be > 1; got {alpha}")

    shape_factor = np.asarray(shape_factor)

    # Ensure output units don't have particle in numerator
    c = c * ureg("1/particle")

    exp = 4 - alpha
    try:
        x_diff = xmax**exp - xmin**exp
    except DimensionalityError as exc:
        raise ValueError(
            "Cannot raise a Quantity to an array exponent. Use a single value for alpha"
            "or remove the units from xmin and xmax.",
        ) from exc
    mass = density * shape_factor * c / exp * x_diff

    return mass


def powerlaw_compute_number(
    xmin: Quantity, xmax: Quantity, alpha: float | ArrayLike, c: Quantity
) -> Quantity:
    """
    Compute number of particles in size range assuming power law size distribution

    Power law number size distribution:
        n(x) = C * x^-alpha

    Args:
        xmin, xmax: Size range bounds
        alpha: Power law parameter alpha, the exponent (must be > 1)
        c: Power law parameter C, the scaling factor

    All arguments must have size 1 or n.

    Returns:
        Number of particles in size range(s) [xmin, xmax]

    Derivation:
                 n(x) = C * x^-alpha
        N(xmin, xmax) = Integral[C * x^-alpha] dx
                      = C / (1 - alpha) * [xmax^(1 - alpha) - xmin^(1 - alpha)]
    """

    alpha = np.asarray(alpha).astype(float)  # numpy disallows negative integer powers
    if np.any(alpha <= 1):
        raise ValueError(f"alpha must be > 1; got {alpha}")

    exp = 1 - alpha
    try:
        x_diff = xmax**exp - xmin**exp
    except DimensionalityError as exc:
        raise ValueError(
            "Cannot raise a Quantity to an array exponent. Use a single value for alpha"
            "or remove the units from xmin and xmax.",
        ) from exc
    number = c / exp * x_diff

    return number


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
