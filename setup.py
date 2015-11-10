"""
Created on Mon Sep 20 15:02:41 2010

@author: Thomas Graff

https://packaging.python.org/en/latest/
https://docs.python.org/2/distutils/index.html
http://pythonhosted.org/setuptools/index.html
https://pypi.python.org/pypi/twine
https://www.pypa.io/en/latest/

run:
 + python setup.py sdist
   to create source distribution

Elements to setup:
 * Generate frozen installation folder with pyinstaller?
 * Generate installation package
 * Generate source distribution - sdist
 * Run test, check?

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
import sys
from os import path
from codecs import open  # To use a consistent encoding
# from pkg_resources import parse_version
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


# import ConsumerCheck


here = path.abspath(path.dirname(__file__))

# Metadatafiles
# README.rst, HISTORY.rst ,AUTHORS.rst

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='ConsumerCheck',

    # Versions should comply with PEP440. For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.3.3',

    description='Software for analysis of sensory and consumer data',
    long_description=long_description,

    # The project's main homepage.
    url='http://sourceforge.net/projects/consumercheck/',

    # Author details
    author='Thomas Graff',
    author_email='graff.thomas@gmail.com',

    # Maintainer details
    maintainer='Oliver Tomic',
    maintainer_email='olivertomic@zoho.com',

    license='GNU GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Natural Language :: English',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],

    # What does your project relate to?
    keywords='statistic education science',

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
    extras_require={
        'dev': ['Sphinx', 'check-manifest'],
        'testing': ['pytest', 'coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here. If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'ConsumerCheck': ['*.svg', '*.png', 'graphics/*.ico', 'rsrc/*.r'],
    },

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
        'console_scripts': [
            'ccrun = ConsumerCheck.cc_start:main',
        ],
        'gui_scripts': [
            'ccgui = ConsumerCheck.cc_start:main',
        ],
        'distutils.commands': [
            'foo = mypackage.some_module:foo',
        ],
    },

    # zip_safe=False,

    cmdclass={'test': PyTest},
    platforms='any',
    test_suite='ConsumerCheck.tests.test_consumercheck',
    tests_require=['pytest'],
)
