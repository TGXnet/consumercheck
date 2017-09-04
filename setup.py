"""
Created on Mon Sep 20 15:02:41 2010

@author: Thomas Graff

https://packaging.python.org/en/latest/
https://docs.python.org/2/distutils/index.html
http://pythonhosted.org/setuptools/index.html
https://pypi.python.org/pypi/twine
https://www.pypa.io/en/latest/
http://python-notes.curiousefficiency.org/en/latest/pep_ideas/core_packaging_api.html

run:
 + python setup.py sdist
   to create source distribution

Elements to setup:
 + Generate frozen installation folder with pyinstaller?
 + Generate installation package
 + Generate source distribution - sdist
 + Run test, check?

Do a release
python setup.py --help-commands
python setup.py sdist upload -r pypitest|pypi
better use
twine for secure uploading (by now)

Look into:
 + pre-sign your files with GPG
 + upload_docs - Upload package documentation to PyPI
 + upload_docs will attempt to run the build_sphinx command to generate uploadable

install: install_lib, install_data, install_scripts

PyPI credentials can be found in: .pypirc

"""
import os
import sys
from codecs import open  # To use a consistent encoding
# from pkg_resources import parse_version
from setuptools import setup, find_packages

import setuputils.commands


here = os.path.abspath(os.path.dirname(__file__))

# Metadatafiles
# README.rst, HISTORY.rst ,AUTHORS.rst


setup(
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['ConsumerCheck', 'ConsumerCheck.tests'],
    # packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    # List run-time dependencies here. These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        # 'numpy',
        # 'traits >=4.4.0, <4.5.0',
        # 'enable >=4.4.0, <4.5.0',	# Require traitsui-4.5.1, PIL
        # 'chaco >=4.4.0, !=4.5.0',
        # 'pandas',			# OK, install but requires numpy
        # 'openpyxl',
        # 'xlrd',
        'pyper >=1.1.1, !=1.1.2',
        'colormath',
        'configparser',
    ],

    # List additional groups of dependencies here (e.g. development dependencies).
    # http://pythonhosted.org/setuptools/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['Sphinx', 'check-manifest'],
    #     'testing': ['pytest', 'coverage'],
    # },

    # setup_requires=[
    #     'pytest-runner >=2.10, <3dev'
    # ],

    # tests_require=[
    #     'pytest'
    # ],

    # python_requires=None,

    # If there are data files included in your packages that need to be
    # installed, specify them here. If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'ConsumerCheck': ['*.svg', '*.png', 'graphics/*.ico', 'rsrc/*.r'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # Automatically include any data files it finds inside your package directories?
    # If you want the files and directories from MANIFEST.in to also be installed
    # (e.g. if it is runtime-relevant data)
    # include_package_data=True,

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # scripts=['consumercheck'],

    # Description here
    # http://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
    entry_points={
        # 'console_scripts': [
        #     'ccrun = ConsumerCheck.cc_start:main',
        # ],
        # 'gui_scripts': [
        #     'ccgui = ConsumerCheck.cc_start:main',
        # ],
        # 'distutils.commands': [
        #     'petter = setuputils.commands.PylintCommand',
        # ],
    },

    cmdclass={
        # 'test': PyTest,
        'pylint': setuputils.commands.PylintCommand,
        'pyinst': setuputils.commands.PyInstallerCommand,
    },
)
