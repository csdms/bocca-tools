from ez_setup import use_setuptools

use_setuptools ()

from setuptools import setup, find_packages

setup (name='BoccaTools',
       version='0.1',
       description='Python utilities for bocca',
       author='Eric Hutton',
       author_email='huttone@colorado.edu',
       url='http://csdms.colorado.edu',
       #packages=find_packages (exclude='tests'),
       packages=['bocca'],
       #package_data={'bocca': 'bocca-build', 'bocca': 'bocca-save'},
       scripts=['scripts/bocca-build', 'scripts/bocca-save']
      )
