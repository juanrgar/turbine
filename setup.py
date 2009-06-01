#!/usr/bin/env python

"""
Installation module for Turbine.
"""

from distutils.core import setup

setup(name='Turbine',
      version='0.1',
      description='GObject Code Generator',
      author=file('AUTHORS').read(),
      url='http://git.gnome.org/cgit/turbine/',
      packages=['turbine'],
      package_dir={'turbine': 'src/turbine'},
      package_data={'turbine': ['*.xml']},
      scripts=['turbine'],
)
