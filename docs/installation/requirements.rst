..  _requirements:

Package dependencies
====================

**MRSimulator** works with Python versions > |PY_VERSION| and is compatible with the
following operating systems:

- MacOS 10.15 or later
- Windows 7 or later
- Most releases of Linux

----

**MRSimulator** depends on the following packages:

**Required packages**

- `numpy>=1.20 <https://www.numpy.org>`_
- `matplotlib>=3.3.4 <https://matplotlib.org>`_ for figures and visualization
- `lmfit>=1.0.3 <https://lmfit.github.io/lmfit-py/>`_ for least-squares fitting
- `pandas>=1.1.3 <https://pandas.pydata.org/docs/>`_
- `csdmpy>=0.7 <https://csdmpy.readthedocs.io/en/stable/>`_
- `pydantic>=2.8 <https://pydantic-docs.helpmanual.io>`_
- `nmrglue>=0.9 <https://nmrglue.readthedocs.io/>`_
- typing-extensions>=3.7
- numexpr>=2.8.4
- psutil>=5.4.8
- joblib>=1.0.0

**Required libraries for local build**

- openblas
- fftw

----

For ``MRSimulator`` developers, the following packages are required:

*For building C libraries*

- cython>=0.29.14

*For unit tests*
- sympy
- pytest<8.0
- pytest-cov
- sybil>=3.0.0

*For formatting*

- black
- pre-commit>=2.11.1

*For building documentation*

- sphinxjp.themes.basicstrap
- sphinx<=6.0
- sphinx-gallery>=0.10
- pillow>=7.1.2
- breathe==4.34.0
- sphinx_copybutton>=0.3.0
- sphinx-tabs>=1.1.13
- recommonmark
- sphinx-version-warning
