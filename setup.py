# -*- coding: utf-8 -*-
"""NetCDFinterface: a python NetCDF API for AHM workflow"""

from setuptools import setup, find_packages

setup(name="NetCDFinterface",
      version=0.01,
      maintainer="Jörg Buchwald",
      maintainer_email="joerg_buchwald@ufz.de",
      author="Jörg Buchwald",
      author_email="joerg.buchwald@ufz.de",
      url="https://github.com/joergbuchwald/NetCDFinterface",
      classifiers=["Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Visualization",
          "Topic :: Scientific/Engineering :: Physics",
          "Topic :: Scientific/Engineering :: Mathematics",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.8"],
      license="MIT -  see LICENSE.txt",
      platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
      include_package_data=True,
      install_requires=["netCDF4", "numpy"],
      py_modules=["NetCDFInterpolate", "NetCDFIO","PVD2netCDF", "PVD2netCDF_ahm","NCFilter"],
      package_dir={'': 'NetCDFinterface'})
