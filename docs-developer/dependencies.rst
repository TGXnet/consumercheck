*********************************
 ConsumerCheck development setup
*********************************

ConsumerCheck (CC) is developed in Python but it also uses the R statistical environment to do some of its calculations.

On Windows there is some scientific Python distributions that includes pretty much everything you need. So you may look into one of these to make your life easier:
- PythonXY
- Enthought Canopy
- Anaconda from Continuum Analytics

On Linux you have to do some mixing and matching using the native package manager and pip.

And on Mac I have no clue what to do.


Manual Python setup
===================

CC is developed using python ver 2.7.x

CC depends on a number of Python libraries. Unfortunately CC does not work with the latest versions of all the libraries so you also have to choose a "good" version when you install the library.

When you use a tool like pip to install a library, pip will also install the libraries that this library depends on. So I will only list the libraries that you manualy hav to install.

======== =========== ==============
 Name     Tested ver  Function
======== =========== ==============
chaco     4.2.0       Plotting library
pandas    0.12.0      Matrix container
numpy     1.8.2       Baisis for statistics and datatype
traits    4.2.0       Event and type automation for Traitsui and Chaco
traitsui  4.2.0       Abstract GUI toolkit
pyface    4.2.0       Traitsui nees this
enable    4.2.0       Support for Chaco
pyparsing 1.5.6       Needed by Enable, not installed automatic by pip
xlrd      0.9.2       For reading XL spredsheet
openpyxl  1.7.0       For reading XL spredsheet
pytest    2.6.3       Testing framework
bbfreeze  1.1.3       Extracting stand alone innstalation for Windows
colormath 1.0.8       Lates is 2.1.0
pyper     1.1.2       Python <-> R communication
wxPython  2.8.x       GUI backend

Dependencies:
chaco: enable
enable: traitsui, pillow(PIL)
traitsui: traits, pyface
traits: -
pyface: pyqt4, wxgtk3.0
pandas: numpy, python-dateutil, pytz
numpy: -


R setup
=======

Some of the statistical modules is written in R statistical language.
So we also need a running R environment.

The Conjoint method depends on the **lmerTest** package.
By now CC is using lmerTest version 2.0-11 (not the latest one) dated 2014-07-24.
This package require R ver 3.0.0 or newer.

The dependencies listed in the lmerTest package is::

 lmerTest:
 Depends: R (>= 3.0.0), Matrix, stats, methods, lme4 (>= 1.0)
 Imports: numDeriv, MASS, Hmisc, gplots, pbkrtest


Othe setup
==========

Windows Installer XML (WiX) toolset v3.6 (beta) is used to generate windows installer.
