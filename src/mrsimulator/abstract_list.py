# -*- coding: utf-8 -*-
from collections import MutableSequence
from itertools import permutations

import numpy as np
from mrsimulator.transition import Transition


__author__ = "Deepansh J. Srivastava"
__email__ = "srivastava.89@osu.edu"

__all__ = ["TransitionList"]


class AbstractList(MutableSequence):
    def __init__(self, data=[]):
        super().__init__()
        self._list = list(data)

    def __repr__(self):
        """String representation"""
        return self.__str__()

    def __str__(self):
        """String representation"""
        string = ",\n".join([item.__repr__() for item in self._list])
        return f"[{string}]"

    def __len__(self):
        """List length"""
        return len(self._list)

    def __getitem__(self, index):
        """Get a list item"""
        return self._list[index]

    def __delitem__(self, index):
        raise LookupError("Deleting items is not allowed.")
        # del self._list[index]

    def insert(self, index, item):
        """Insert a list item"""
        self._list.insert(index, item)

    def append(self, item):
        """Append a list item"""
        self.insert(len(self._list), item)

    def __eq__(self, other):
        """Check equality of DependentVariableList."""
        if not isinstance(other, self.__class__):
            return False
        if len(self._list) != len(other._list):
            return False

        check = []
        for i in range(len(self._list)):
            check.append(self._list[i] == other._list[i])

        if np.all(check):
            return True
        return False


class TransitionList(AbstractList):
    def __init__(self, data=[]):
        super().__init__(data)

    def __setitem__(self, index, item):
        if isinstance(item, dict):
            item = Transition(**item)
        if not isinstance(item, Transition):
            raise ValueError(
                f"Expecting a Transition object, found {item.__class__.name__}"
            )
        self._list[index] = item

    def Zeeman_allowed(self):
        return TransitionList([item for item in self._list if item.Zeeman_allowed])

    def filter(self, P=None, D=None, transitions=None, start_state=None, isotopes=None):
        """Filter a list of transitions to satisfy the filtering criterion.
            Args:
                P: A list of Δm values. If `l` Δm are given for an isotopomer with N
                    sites, where N >= l, the transitions corresponding to all
                    combinations of `l` Δm values over N sites is selected.
                delta_ms: A list of Δm values for the spin transition.
                transition: A list of single spin transition corresponding to each site
                    in the isotopomer.
                isotopes: A dictionary containing the method isotopes and the list of
                    isotopes in the isotopomer.
        """

        if P is transitions is start_state is None:
            P = -1
        ts = self._list.copy()

        # if search is None:
        if P is not None:
            ts = TransitionList([item for item in ts if np.allclose(item.P, P)])
        if transitions is not None:
            for transition in transitions:
                ts = TransitionList(
                    [item for item in ts if item == Transition(**transition)]
                )
        if start_state is not None:
            ts = [item for item in ts if ts.initial == start_state]
        return ts

        # lst = self._list
        # for i, element in enumerate(search):
        #     if isinstance(element, int):
        #         lst = [item for item in lst if item.delta_m(i) == element]
        #     if isinstance(element, list):
        #         lst = [
        #             item
        #             for item in lst
        #             if (item.initial[i] == element[1] and item.final[i] == element[0])
        #         ]
        # return lst
        #     return TransitionList(
        #         [item for item in self._list if np.all(item.initial == delta_ms)]
        #     )

        # if delta_ms is not None:
        #     return TransitionList(
        #         [item for item in self._list if np.all(item.delta_ms == delta_ms)]
        #     )
        # return TransitionList([item for item in self._list if item.p == p])


# class DependentVariableList(AbstractList):
#     def __init__(self, data=[]):
#         super().__init__(data)

#     def __setitem__(self, index, item):
#         if not isinstance(item, DependentVariable):
#             raise ValueError(
#                 f"Expecting a DependentVariable object, found {item.__class__.name__}"
#             )
#         self._list[index] = item
