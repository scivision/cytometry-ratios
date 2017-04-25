#!/usr/bin/env python
req = ['nose','numpy','matplotlib','seaborn','scikit-image','scipy','pillow','pathlib2']
pipreq = ['tifffile']
# %%
import pip
try:
    import conda.cli
    conda.cli.main('install',*req)
except Exception as e:
    pip.main(['install'] + req)
pip.main(['install'] + pipreq)
# %%
from setuptools import setup

setup(name='pycyto',
      packages=['pycyto'],
      author='Michael Hirsch, Ph.D.',
      version='0.1',
      url='https://github.com/scivision/cytometry-ratios',
      description='prototyping of whole slide cytometer',
    )
