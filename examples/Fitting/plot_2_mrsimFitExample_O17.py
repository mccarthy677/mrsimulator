#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fitting Sodium Silicate.
^^^^^^^^^^^^^^^^^^^^^^^^
"""
# sphinx_gallery_thumbnail_number = 3
#%%
# Often, after obtaining an NMR measurement we must fit tensors to our data so we can
# obtain the tensor parameters. In this example, we will illustrate the use of the *mrsimulator*
# method to simulate the experimental spectrum and fit the simulation to the data allowing us to
# extract the tensor parameters for our isotopomers. We will be using the *LMFIT* methods to
# establish fitting parameters and fit the spectrum. The following examples will show fitting with
# two synthetic :math:`^{29}\text{Si}` spectra--cuspidine and wollastonite--as well as the
# measurements from an :math:`^{17}\text{O}` experiment on :math:`\text{Na}_{2}\text{SiO}_{3}`.
# The *mrsimulator* library and data make use of CSDM compliant files.
# In this example we will fit a simulation to an experimentally obtained :math:`^{17}\text{O}` spectrum.
#
# Begin by importing *csdmpy* and loading the data file. We will also be establishing *matplotlib*
# figure size here.
import csdmpy as cp
import matplotlib.pylab as pylab

params = {"figure.figsize": (4.5, 3), "font.size": 9}
pylab.rcParams.update(params)


filename = "https://osu.box.com/shared/static/kfgt0jxgy93srsye9pofdnoha6qy58qf.csdf"
oxygen_experiment = cp.load(filename).real

cp.plot(oxygen_experiment)

#%%
# Next, we will want to create a ``simulation`` object that we will use to fit to our
# spectrum. We will need to import the necessary libraries for the *mrsimulator*
# methods. We will then create ``isotopomer`` objects.

#%%


from mrsimulator import Simulator, Isotopomer, Site, Dimension
from mrsimulator import SymmetricTensor as st
from mrsimulator.methods import one_d_spectrum

sim = Simulator()
O17_1 = Site(
    isotope="17O",
    isotropic_chemical_shift=60.0,
    quadrupolar={"Cq": 4200000, "eta": 0.5},
)
O17_2 = Site(
    isotope="17O", isotropic_chemical_shift=40, quadrupolar={"Cq": 2400000, "eta": 0.18}
)

isotopomers = [Isotopomer(sites=[site]) for site in [O17_1, O17_2]]

dimension = Dimension(
    isotope="17O",
    magnetic_flux_density=9.4,  # in T
    number_of_points=oxygen_experiment.dimensions[0].count,  # 2046,
    spectral_width=oxygen_experiment.dimensions[0].count
    * oxygen_experiment.dimensions[0].increment.to("Hz").value,  # 20000, # in Hz
    reference_offset=oxygen_experiment.dimensions[0]
    .coordinates_offset.to("Hz")
    .value,  # 1220.7031, # in Hz
    rotor_frequency=14000,  # in Hz
)

sim.isotopomers += isotopomers
sim.dimensions += [dimension]
sim.run(method=one_d_spectrum)
sim_data = sim.as_csdm_object()

cp.plot(sim_data)

#%%
# Once we have our simulation we must create our list of parameters to use in our
# fitting. We will be using the ``Parameters()`` class from *LMFIT*.

from lmfit import Minimizer, Parameters, report_fit

params = Parameters()

#%%
# In each experiment the number of isotopomers and sites present as well as their
# attributes may vary. To simplify the parameter list creation we will use the
# *make_fitting_parameters()* method from *mrsimulator.spectral_fitting*

#%%


from mrsimulator import spectral_fitting

params = spectral_fitting.make_fitting_parameters(sim)
params.add(
    name="sigma", value=oxygen_experiment.dimensions[0].increment.to("Hz").value, min=0
)
params.add(name="factor", value=oxygen_experiment.max(), min=0)

#%%
# With an experimental spectrum, a simulaton, and a list of parameters we are now
# ready to perform a fit. This fit will be performed using the *LMFIT* library as
# well as our *fcn2min* function from *mrsimulator.spectral_fitting*. The arguments
# for *fcn2min* are the intensities from the experimental data and the simulation
# CSDM object. Reporting the results of the fit will give us our tensor parameters.
#
# One thing to note is that the names of our parameters must correspond to their addresses within the simulation object
# in order to update the simulation during the fit. The *LMFIT* library does not allow for the use of special characters
# such as "\[", "\]", or "." so our current workaround is converting the special characters to their corresponding HTML
# character code numbers and converting back to the special character when updating the simulation.


#%%


minner = Minimizer(
    spectral_fitting.min_function,
    params,
    fcn_args=(oxygen_experiment, sim, "Lorentzian"),
)
result = minner.minimize()
report_fit(result)

#%%
# Next, we can compare the fit to the experimental data using the *matplotlib* library:

#%%

import matplotlib
import matplotlib.pyplot as plt


plt.figsize = (4, 3)
residual = oxygen_experiment.copy()
residual[:] = result.residual
plt.plot(*oxygen_experiment.to_list(), label="Spectrum")
plt.plot(*(oxygen_experiment - residual).to_list(), "r", alpha=0.5, label="Fit")
plt.plot(*residual.to_list(), alpha=0.5, label="Residual")

plt.xlabel("Frequency / Hz")
plt.grid(which="major", axis="both", linestyle="--")
plt.legend()

plt.tight_layout()
plt.show()