#!/usr/bin/env python
from setuptools import setup

req = ['nose','numpy','matplotlib','seaborn','scikit-image','pathlib2']

setup(name='pycyto',
      packages=['pycyto'],
      url='https://github.com/scienceopen/cytometry-ratios',
      description='prototyping of whole slide cytometer',
      install_requires=req,
    )
