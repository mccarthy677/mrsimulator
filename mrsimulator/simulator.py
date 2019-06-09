# -*- coding: utf-8 -*-
from .unit import _ppm
from .unit import string_to_quantity
from .utils import __get_spin_attribute__

try:
    import csdfpy as cp
except ImportError:
    pass


__author__ = "Deepansh J. Srivastava"
__email__ = ["srivastava.89@osu.edu", "deepansh2012@gmail.com"]


class _Dimensions:
    __slots__ = ()

    def __new__(
        number_of_points=1024,
        spectral_width="100 kHz",
        reference_offset="0 Hz",
    ):
        """Initialize."""
        dictionary = {}
        dictionary["number_of_points"] = int(number_of_points)

        spectral_width = string_to_quantity(spectral_width)
        if spectral_width.unit.physical_type != "frequency":
            raise Exception(
                ("A frequency value is required for the 'spectral_width'.")
            )
        dictionary["spectral_width"] = spectral_width.to("Hz").value

        reference_offset = string_to_quantity(reference_offset)
        if reference_offset.unit.physical_type != "frequency":
            raise Exception(
                ("A frequency value is required for the 'reference_offset'.")
            )
        dictionary["reference_offset"] = reference_offset.to("Hz").value
        return dictionary


class _Spectrum(_Dimensions):
    """Set up a virtual spin environment."""

    __slots__ = ()

    def __new__(
        self,
        magnetic_flux_density="9.4 T",
        rotor_frequency="0 kHz",
        rotor_angle="54.735 deg",
        rotor_phase="0 rad",
        nucleus="1H",
        *args,
        **kwargs,
    ):
        """Initialize"""
        dimension_dictionary = super(_Spectrum, self).__new__(*args, **kwargs)
        magnetic_flux_density = string_to_quantity(magnetic_flux_density)
        if magnetic_flux_density.unit.physical_type != "magnetic flux density":
            raise Exception(
                (
                    "A magnetic flux density quantity is required for "
                    "'magnetic_flux_density'."
                )
            )
        magnetic_flux_density = magnetic_flux_density.to("T").value

        rotor_frequency = string_to_quantity(rotor_frequency)
        if rotor_frequency.unit.physical_type != "frequency":
            raise Exception(
                ("A frequency quantity is required for 'rotor_frequency'.")
            )
        rotor_frequency = rotor_frequency.to("Hz").value

        rotor_angle = string_to_quantity(rotor_angle).to("rad").value
        rotor_phase = string_to_quantity(rotor_phase).to("rad").value

        dictionary = {
            "magnetic_flux_density": magnetic_flux_density,
            "rotor_frequency": rotor_frequency,
            "rotor_angle": rotor_angle,
            "rotor_phase": rotor_phase,
        }

        dictionary.update(dimension_dictionary)

        detect = get_proper_detector_nucleus(nucleus)
        try:
            spin_dictionary = __get_spin_attribute__[detect]
            spin_dictionary["isotope"] = detect
        except KeyError:
            raise Exception(f"Failed to simulates the {detect} spectrum.")

        dictionary.update(spin_dictionary)
        return dictionary


# class Isotopomers(list):
#     def __init__(self, isotopomers: list) -> list:
#         isotopomers_ = _Isotopomers(isotopomers)
#         list.__init__(self, isotopomers_)

#     def append(self, value):
#         isotopomer_ = _Isotopomer(**value)
#         list.append(isotopomer_)


class _Isotopomers:
    __slots__ = ()

    def __new__(self, isotopomers: list) -> list:

        if not isinstance(isotopomers, list):
            raise Exception(
                (
                    f"A list of isotopomers is required, "
                    f"found {type(isotopomers)}."
                )
            )
        if len(isotopomers) != 0:
            if not isinstance(isotopomers[0], dict):
                raise Exception(
                    (
                        f"A list of isotopomer dictionaries is "
                        f"required, found {type(isotopomers[0])}."
                    )
                )

        isotopomers_ = []
        for isotopomer in isotopomers:
            isotopomer_set = _Isotopomer(**isotopomer)
            isotopomers_.append(isotopomer_set)

        return isotopomers_


class _Isotopomer:
    __slots__ = ()

    def __new__(
        self,
        sites: list = [],
        couplings: list = [],
        abundance: str = "100.0 %",
    ) -> list:
        """Initialize."""
        if not isinstance(sites, list):
            raise ValueError(
                (f"Expecting a list of sites. Found {type(sites)}.")
            )
        _sites = []
        abundance = string_to_quantity(abundance).to("").value
        for site in sites:
            _sites.append(_Site(**site))
        return {"sites": _sites, "abundance": abundance}


def _check_values_in_ppm(value, property):
    value_ = string_to_quantity(value)
    if value_.unit.physical_type == "dimensionless":
        if str(value_.unit) == "ppm":
            return value_
        else:
            return value_.to(_ppm)
    if value_.unit.physical_type == "frequency":
        return value_
    else:
        raise Exception(
            (
                f"Expecting '{property}' in units of frequency or a "
                f"dimensionless frequency ratio, ppm, found {str(value_)}."
            )
        )


class _Site:
    __slots__ = ()

    def __new__(
        self,
        isotope_symbol="1H",
        isotropic_chemical_shift="0 ppm",
        shielding_symmetric=None,
    ):
        """Initialize."""
        return {
            "isotope_symbol": isotope_symbol,
            "isotropic_chemical_shift": _check_values_in_ppm(
                isotropic_chemical_shift, "isotropic_chemical_shift"
            ),
            "shielding_symmetric": {
                "anisotropy": _check_values_in_ppm(
                    shielding_symmetric["anisotropy"], "shielding anisotropy"
                ),
                "asymmetry": float(shielding_symmetric["asymmetry"]),
            },
        }


def get_proper_detector_nucleus(string):
    numeric = "0123456789"
    for i, c in enumerate(string):
        if c in numeric:
            break
    return string[i:] + string[0:i]


def get_csdfpy_object(x, x0, y, application):
    ob1 = cp.new()
    d1 = {
        "type": "linear",
        "number_of_points": x.size,
        "increment": str(x[1] - x[0]),
        "index_zero_value": str(x[0]),
        "origin_offset": str(x0),
        "quantity": "frequency",
    }
    ob1.add_dimension(d1)
    s1 = {
        "type": "internal",
        "numeric_type": "float64",
        "components": [y],
        "component_labels": ["arbitrary units"],
    }
    ob1.add_dependent_variable(s1)

    ob1.dependent_variables[0].application = {"mrsimulator": application}
    return ob1


# class _dimension_object:
#     __slots__ = (
#         'type',
#         'number_of_points',
#         'increment',
#         'index_zero_value',
#         'origin_offset',
#         'coordinates'
#     )

#     def __init__(self, vector, origin_offset):
#         self.type= 'linear'
#         self.number_of_points = vector.size
#         self.increment = str(vector[1] - vector[0]) + ' Hz'
#         self.index_zero_value = str(vector[0]) + ' Hz'
#         self.origin_offset = str(origin_offset) + ' MHz'
#         self.coordinates = vector

#     def to_ppm(self):
#         return None


def _simulator(spectrum, method, isotopomers, **kwargs):
    """Execute the method and acquire a spectrum.

    :param method: A function describing the pulse sequence.
    :param sample: A python dictionary describing the sample;

    :returns: freq: A numpy array of frequency values.
    :returns: amp:  A numpy array of amplitudes corresponding to
                    the frequencies.

    """
    if isotopomers is None:
        raise Exception("No isotopomer found.")
    isotopomers = _Isotopomers(isotopomers)

    spectrum = _Spectrum(**spectrum["direct_dimension"])
    # print(spectrum)

    freq, amp = method(spectrum=spectrum, isotopomers=isotopomers, **kwargs)

    return (freq, amp)