# -*- coding: utf-8 -*-
from copy import deepcopy
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional

from mrsimulator import Parseable
from mrsimulator.site import Site
from pydantic import Field
from mrsimulator.dimension import ISOTOPE_DATA

__author__ = "Deepansh J. Srivastava"
__email__ = ["srivastava.89@osu.edu", "deepansh2012@gmail.com"]


class Isotopomer(Parseable):
    """
    Base isotopmer class representing an isolated spin-system with sites and couplings.

    Arguments:
        name: An optional string with the isotopomer name. The default is an empty
                string.
        description: An optional string describing the isotopomer. The default is
                an empty string.
        sites: A list of :ref:`site_api` objects or an equivalent python dict object
                representing a nuclear site. Default value is an empty list.
        abundance: The abundance of the isotopomer in unit of %. The default value is
                100. This attribute is useful when multiple isotopomers are present.
    """

    name: Optional[str] = ""
    description: Optional[str] = ""
    sites: List[Site] = []
    # couplings: list = [], # TODO: Deepansh what should this look like?
    abundance: float = Field(default=100, ge=0, le=100)

    property_unit_types: ClassVar = {"abundance": "dimensionless"}
    property_default_units: ClassVar = {"abundance": "pct"}
    property_units: Dict = {"abundance": "pct"}

    @classmethod
    def parse_dict_with_units(cls, py_dict):
        """
        Parse physical quantity from the attributes of an isotopomer object
        expressed as a python dictionary. The physical quantities are expressed
        as string with a number followed by a unit.

        Args:
            py_dict: Python dictionary representation of an isotopomer object with
                    attributes values as string with a physical quantity.

        Example:
            >>> isotopomer_dict = {
            ...     "sites": [{
            ...         "isotope":"13C",
            ...         "isotropic_chemical_shift": "20 ppm",
            ...         "shielding_symmetric": {
            ...             "zeta": "10 ppm",
            ...             "eta": 0.5
            ...         }
            ...     }]
            ... }
            >>> isotopomer_1 = Isotopomer.parse_dict_with_units(isotopomer_dict)
        """
        py_dict_copy = deepcopy(py_dict)
        if "sites" in py_dict_copy:
            py_dict_copy["sites"] = [
                Site.parse_dict_with_units(s) for s in py_dict_copy["sites"]
            ]

        return super().parse_dict_with_units(py_dict_copy)

    def to_freq_dict(self, B0):
        """
        Serialize the Isotopomer object to a JSON compliant python dictionary where the
        attribute values are numbers expressed in default units. The default unit
        for attributes with respective dimensionalities are:
        - frequency: `Hz`
        - angle: `rad`

        Args:
            B0: The macroscopic magnetic flux density in units of Tesla, T.

        Return: A python dict

        Example:
            >>> from pprint import pprint
            >>> pprint(isotopomer_1.to_freq_dict(B0=9.4))
            {'abundance': 100,
             'description': '',
             'name': '',
             'sites': [{'isotope': '13C',
                        'isotropic_chemical_shift': -2013.1791999999998,
                        'quadrupolar': None,
                        'shielding_antisymmetric': None,
                        'shielding_symmetric': {'alpha': None,
                                                'beta': None,
                                                'eta': 0.5,
                                                'gamma': None,
                                                'zeta': -1006.5895999999999}}]}
        """
        temp_dict = self.dict()
        temp_dict["sites"] = [site.to_freq_dict(B0) for site in self.sites]
        temp_dict.pop("property_units")
        return temp_dict

    def to_dict_with_units(self):
        """
        Serialize the Isotopomer object to a JSON compliant python dictionary object
        where attribute values are physical quantities expressed as a string with a
        number followed by a unit.

        Return: A python dict

        Example:
            >>> from pprint import pprint
            >>> pprint(isotopomer_1.to_dict_with_units())
            {'abundance': '100%',
             'description': '',
             'name': '',
             'sites': [{'isotope': '13C',
                        'isotropic_chemical_shift': '20.0 ppm',
                        'shielding_symmetric': {'eta': 0.5, 'zeta': '10.0 ppm'}}]}
        """
        temp_dict = self.dict()
        temp_dict["sites"] = [site.to_dict_with_units() for site in self.sites]
        temp_dict["abundance"] = f"{self.abundance}%"
        temp_dict.pop("property_units")

        return temp_dict

    def get_isotopes(self, I=None):
        """
        Set of unique isotopes from the list of sites corresponding to the given value
        of `I`. If `I` is unspecified or None, a set of all defined isotopes is
        returned instead.

        Args:
            I: (optional) The spin quantum number. Valid input are multiples of 0.5.

        Returns:
            A set

        Example:
            >>> isotopomers.get_isotopes() # doctest:+SKIP
            {'1H', '27Al', '13C'}
            >>> isotopomers.get_isotopes(I=0.5) # doctest:+SKIP
            {'1H', '13C'}
            >>> isotopomers.get_isotopes(I=1.5)
            set()
            >>> isotopomers.get_isotopes(I=2.5)
            {'27Al'}
        """
        return set(
            site.isotope for site in self.sites if site.isotope in allowed_isotopes(I)
        )


def allowed_isotopes(I=None):
    """
    List of NMR active isotopes currently supported in ``mrsimulator``.

    Args:
        I: (optional) The spin quantum number. Valid input are multiples of 0.5.

    Returns:
        A list of all isotopes supported in ``mrsimulator`` with the given spin
        quantum number `I`. If the spin is unspecified or None, a list of all
        allowed isotopes is returned instead.
    Returns:
        Set
    """
    if I is None:
        return list({isotope for isotope, data in ISOTOPE_DATA.items()})
    return list(
        {
            isotope
            for isotope, data in ISOTOPE_DATA.items()
            if data["spin"] == int(2 * I)
        }
    )
