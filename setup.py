#!/usr/bin/env python
install_requires = ['numpy','matplotlib','seaborn','scikit-image','scipy','imageio','tifffile']
# %%
from setuptools import setup, find_packages

setup(name='pycyto',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      version='0.1.0',
      url='https://github.com/scivision/cytometry-ratios',
      description='prototyping of whole slide cytometer',
      long_description=open('README.rst').read(),
      install_requires=install_requires,
      python_requires=">=3.5",
    )
