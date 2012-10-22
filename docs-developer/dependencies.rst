============================
 ConsumerCheck dependencies
============================

Python libraries

======== =========== ==============
 Name     Tested ver  Function
======== =========== ==============
numpy     1.6.2       Baisis for statistics and datatype
traits    4.2.0       Event and type automation for Traitsui and Chaco
traitsui  4.2.0       Abstract GUI toolkit
pyface    4.2.0       Traitsui nees this
PySide    1.1.2       Python QT GUI toolkit backend
chaco     4.2.0       Plotting library
enable    4.2.0       Support for Chaco
pyparsing 1.5.6       Needed by Enable, not installed automatic by pip
xlrd      0.8.0       For reading XL spredsheet
openpyxl  1.5.8       For reading XL spredsheet
pytest    2.2.4       Testing framework
pandas    0.8.0       Matrix container
bbfreeze  1.0.0       Extracting stand alone innstalation for Windows


To build and install some Python libraries some tools and development libraries
have to be installed on the development system


=============== ===========
Package          Needed by
=============== ===========
deb:cmake         PySide
deb:libqt4-dev    PySide
deb:swig          Enable


wxPython is by now installed globaly on the development system.
But the plan is to be independent from this GUI toolkit.


Some of the statistical modules is written in R statistical language.
So we also need a running R environment.

Last R ver tested is 2.14.1.

Needed R packages.

========= ================
Name       Description
========= ================
mixmod     From Alexandra


Windows Installer XML (WiX) toolset v3.6 (beta) is used to generate windows installer.
