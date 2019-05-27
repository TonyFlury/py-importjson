#!/usr/bin/env python
# coding=utf-8
"""
Implementation of setup.py for importjson library
    ....
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '15 Oct 2015'

import sys

major, minor, micro = sys.version_info[:3]

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

#with open(path.join(here,'requirements.txt'),'r') as dev_req,\
#    open(path.join(here, 'test_requirements.txt'), 'r') as test_req:
#    ir = dev_req.readlines()
#    tr = test_req.readlines()

ir = ['six>=1.10','templatelite>=0.2.1']
tr = ['six>=1.10','templatelite>=0.2.1','click','TempDirectoryContext>=1.0.1']

def extract_version_info( line):
    return line.split('=')[-1].strip().strip('\'\"')

with open(path.join(here, 'importjson/version.py'),'r') as version_fp:
    version, release = None, None
    for line in version_fp:
        version = extract_version_info(line) if version is None and line.startswith('__version__') else version
        release = extract_version_info(line) if release is None and line.startswith('__release__') else release

setup(
    name='importjson',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='Import a json file as a fully functional module '
                'with classes, inheritance, attributes, properties '
                'and constraints',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/TonyFlury/py-importjson',

    # Author details
    author='Anthony Flury',
    author_email='anthony.flury@btinternet.com',

    # Choose your license
    license='GNU General Public License (GPL)',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License (GPL)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        #        'Programming Language :: Python :: 2',
        #        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # What does your project relate to?
    keywords='json development data',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['test*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=ir,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'test': tr,
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={'importjson': ['templates/*.tmpl']},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
    },
    test_suite='tests',
    tests_require=['flake8']
)

