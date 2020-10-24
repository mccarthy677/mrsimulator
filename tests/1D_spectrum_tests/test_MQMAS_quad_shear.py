# -*- coding: utf-8 -*-
"""Lineshape Test."""
import numpy as np
from mrsimulator import Simulator
from mrsimulator import Site
from mrsimulator import SpinSystem
from mrsimulator.methods import FiveQ_VAS
from mrsimulator.methods import Method1D
from mrsimulator.methods import SevenQ_VAS
from mrsimulator.methods import ThreeQ_VAS

method_class = [ThreeQ_VAS, FiveQ_VAS, SevenQ_VAS]


def setup_simulation(site, affine_matrix, class_id=0):

    isotope = site.isotope.symbol
    spin_system = [SpinSystem(sites=[site])]

    method_C = method_class[class_id]

    method = method_C(
        channels=[isotope],
        magnetic_flux_density=7,  # in T
        rotor_angle=54.735 * np.pi / 180,
        spectral_dimensions=[
            {
                "count": 512,
                "spectral_width": 4e4,  # in Hz
                "reference_offset": -3e3,  # in Hz
            },
            {
                "count": 1024,
                "spectral_width": 1e4,  # in Hz
                "reference_offset": -4e3,  # in Hz
            },
        ],
        affine_matrix=affine_matrix,
    )

    method_1 = Method1D(
        channels=[isotope],
        magnetic_flux_density=7,  # in T
        rotor_angle=54.735 * np.pi / 180,
        rotor_frequency=1e9,
        spectral_dimensions=[
            {
                "count": 1024,
                "spectral_width": 1e4,  # in Hz
                "reference_offset": -4e3,  # in Hz
                "events": [
                    {"fraction": 27 / 17, "freq_contrib": ["Quad2_0"]},
                    {"fraction": 1, "freq_contrib": ["Quad2_4"]},
                ],
            }
        ],
    )

    sim = Simulator()
    sim.spin_systems = spin_system  # add the spin-system
    sim.methods = [method, method_1]  # add the method

    # run the simulation
    sim.config.number_of_sidebands = 1
    sim.run()

    csdm_data1 = sim.methods[0].simulation.real.sum(axis=1)
    csdm_data2 = sim.methods[1].simulation.real
    csdm_data1 /= csdm_data1.max()
    csdm_data2 /= csdm_data2.max()

    np.testing.assert_almost_equal(
        csdm_data1.y[0].components, csdm_data2.y[0].components, decimal=3
    )


def test_three_half():
    site = Site(
        isotope="87Rb",
        isotropic_chemical_shift=-38.5,  # in ppm
        quadrupolar={"Cq": 1.94e6, "eta": 1.0},  # Cq is in Hz
    )
    setup_simulation(site, affine_matrix=[9 / 16, 7 / 16, -8 / 17, 1])


def test_five_half():
    site = Site(
        isotope="27Al",
        isotropic_chemical_shift=64.5,  # in ppm
        quadrupolar={"Cq": 3.22e6, "eta": 0.66},  # Cq is in Hz
    )
    # 3Q-MAS
    affine_matrix = [12 / 31, 19 / 31, 31 / 17, 1]
    setup_simulation(site, affine_matrix=affine_matrix)

    # 5Q-MAS
    affine_matrix = [12 / 37, 25 / 37, -37 / 85, 1]
    setup_simulation(site, affine_matrix=affine_matrix, class_id=1)


def test_seven_half():
    site = Site(
        isotope="51V",
        isotropic_chemical_shift=37.4,  # in ppm
        quadrupolar={"Cq": 6.68e6, "eta": 0.2},  # Cq is in Hz
    )
    # 3Q-MAS
    affine_matrix = [45 / 146, 101 / 146, 73 / 17, 1]
    setup_simulation(site, affine_matrix=affine_matrix)

    # 5Q-MAS
    affine_matrix = [9 / 20, 11 / 20, 10 / 17, 1]
    setup_simulation(site, affine_matrix=affine_matrix, class_id=1)

    # 7Q-MAS
    affine_matrix = [45 / 206, 161 / 206, -103 / 238, 1]
    setup_simulation(site, affine_matrix=affine_matrix, class_id=2)