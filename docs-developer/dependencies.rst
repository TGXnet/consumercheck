*********************************
 ConsumerCheck installation setup
*********************************

This description is for those users who wish or need to run the ConsumerCheck (CC) source code directly on their respective OS. CC was successfully tested on Linux and Windows, however we have not tested it on Mac OS.

CC is developed in Python but it also uses the R statistical environment for some statistical analyses. This means that Python and a number of specific Python packages need to be installed, as well as R and some specific R packages. Below follows a description of what installations are needed to make CC source code run on you OS.


=======
CONTENT
=======

(A) 	* LIST OF REQUIRED SOFTWARE INSTALLATIONS
(A1)		- Required Python version
(A2)		- Required Python packages
(A3)		- Required R version
(A4)		- Required R packages

(B)		* HOW TO INSTALL REQUIRED SOFTWARE
(B1)		- Installation of Python and Python packages (You don't have Python installed your machine yet)
(B2)		- Installation of Python packages using the pip installer tool  (You already have Python installed your machine)
(B3)		- Installation of R
(B4)		- Installation of R package 'lmerTest'

(C) 	* DEVELOMENT TOOLS


===========================================
(A) LIST OF REQUIRED SOFTWARE INSTALLATIONS
===========================================

(A1) Required Python version
----------------------------
CC was developed using Python 2.7, meaning that this version needs to be installed on your OS.


(A2) Required Python packages
-----------------------------
CC depends on a number of scientific Python packages. Unfortunately CC does not work with the latest versions of all the packages so you also have to install specific versions of each library.

======== =========== ==============
 Name     Tested ver  Function
======== =========== ==============
chaco     4.4.1       Plotting library
pandas    0.12.0      Matrix container
numpy     1.8.2       Baisis for statistics and datatype
traits    4.5.0       Event and type automation for Traitsui and Chaco
traitsui  4.4.0       Abstract GUI toolkit
pyface    4.4.0       Traitsui nees this
enable    4.4.1       Support for Chaco
pyparsing 1.5.6       Needed by Enable, not installed automatic by pip
xlrd      0.9.2       For reading XL spredsheet
openpyxl  1.7.0       For reading XL spredsheet
colormath 1.0.8       Latest version 2.1.0
pyper     1.1.1       Python <-> R communication
wxPython  2.8.12.1    GUI backend

Dependencies:
chaco: enable
enable: traitsui, pillow(PIL)
traitsui: traits, pyface
traits: -
pyface: pyqt4, wxgtk3.0
pandas: numpy, python-dateutil, pytz
numpy: -


(A3) Required R version
-----------------------
Some of the statistical functions used in CC are written in the R language which is why R needs to be installed on your OS.
R version 3.0.0 or higher


(A4) Required R packages
------------------------
lmerTest



====================================
(B) HOW TO INSTALL REQUIRED SOFTWARE
====================================

If you don't have Python installed on your machine, we recommend to go for installation option (B1). If you have Python installed already, you may go for option (B2) and install missing packages from the list in (A2) using the pip package installer tool. Read these guides if you have not used pip before.
> Full documentation (https://pip.pypa.io/en/latest/)
> Quickstart guide (https://pip.pypa.io/en/latest/quickstart.html)
> Examples (https://pip.pypa.io/en/latest/reference/pip_install.html#examples).


(B1) Installation of Python and Python packages (You don't have Python installed your machine yet)
-----------------------------------------------
We recommend installing Python and Python packages using ONE of the following three free Python distributions (options) listed below. Since none of the three distributions (options) contain all packages you'll have to install some packages afterwards using the pip package installer tool. Read this guide if you have not used pip before 

> Full documentation (https://pip.pypa.io/en/latest/)
> Quickstart guide (https://pip.pypa.io/en/latest/quickstart.html)
> Examples (https://pip.pypa.io/en/latest/reference/pip_install.html#examples).

(Option 1) Anaconda by Continuum Analytics (http://continuum.io/downloads)
  * Available for Windows, Linux and Mac
  * The following Python packages are required for CC, but are missing in the current Anaconda Python distribution (v. 2.1 - released Sep. 30, 2014). They need to be installed by using the pip installer tool after installation of the Anaconda distribution.
     > bbfreeze(https://pypi.python.org/pypi/bbfreeze/1.1.3)
	 > colormath(https://pypi.python.org/pypi/colormath/2.1.0)
	 > PypeR(https://pypi.python.org/pypi/PypeR/1.1.2)
	 > wxpython

(Option 2) PythonXY (https://code.google.com/p/pythonxy/)
  * Available for Windows only
  * The following Python packages are required for CC, but are missing in the current PythonXY distribution (v. 2.7.9.0 - released Dec. 16, 2014). They need to be installed by using the pip installer tool after installation of the PythonXY distribution.
     > bbfreeze(https://pypi.python.org/pypi/bbfreeze/1.1.3)
	 > colormath(https://pypi.python.org/pypi/colormath/2.1.0)
	 > pyface (https://pypi.python.org/pypi/pyface/4.4.0)
	 > PypeR (https://pypi.python.org/pypi/PypeR/1.1.2)

(Option 3) Canopy Express by Enthought (https://store.enthought.com/downloads/)
  * Availabe for Windows, Linux and Mac.
  * The following Python packages are required for CC, but are missing in the current Canopy Express distribution (v. 1.5.2 - released Jan. 30, 2015). They need to be installed by using the pip installer tool after installation of the Canopy Express distribution.
     > bbfreeze(https://pypi.python.org/pypi/bbfreeze/1.1.3)
	 > colormath(https://pypi.python.org/pypi/colormath/2.1.0)
	 > openpyxl(https://pypi.python.org/pypi/openpyxl/2.1.4)
	 > PypeR (https://pypi.python.org/pypi/PypeR/1.1.2)
	 > xlrd (https://pypi.python.org/pypi/xlrd/0.9.3)


(B2) Installation of Python packages using the pip installer tool  (You already have Python installed your machine)
-----------------------------------------------------------------
Install the Python packages that are missing on your machine. You need to have all packages installed that are listed in section (A2).

How to check which Python packages and which version of those are already installed on your machine? Type at the command line:

pip list

More information on pip
> Full documentation (https://pip.pypa.io/en/latest/)
> Quickstart guide (https://pip.pypa.io/en/latest/quickstart.html)
> Examples (https://pip.pypa.io/en/latest/reference/pip_install.html#examples).


Remarks for Linux
.................
On Linux you need to install specific version of the Python packages using the native package manager or pip.


Remarks for Mac
...............
As mentioned above, we haven't tested CC on Mac so far, but you can try . We would be glad to hear from you if you made CC run on Mac.
- Anaconda by Continuum Analytics (http://continuum.io/downloads)
- Canopy Express by Enthought (https://store.enthought.com/downloads/)


(B3) Installation of R (if you don't have it installed on your machine already)
----------------------
Download and install R for your OS (http://cran.r-project.org/). Install R 3.0.0 or higher.


(B4) Installation of R package 'lmerTest'
-----------------------------------------
The Conjoint method in CC depends on the **lmerTest** package.
Install the lmerTest package (http://cran.r-project.org/web/packages/lmerTest/index.html).


CC 1.1.0 uses the R package lmerTest version 2.0-11 (NOT the latest one: 2.0-20 dated 2014-11-22).
This package requires R ver 3.0.0 or newer.

The dependencies listed in the lmerTest package are:

lmerTest:
Depends: R (>= 3.0.0), Matrix, stats, methods, lme4 (>= 1.0)
Imports: numDeriv, MASS, Hmisc, gplots, pbkrtest


=====================
(C) Development tools
=====================

========= =========== ==============
 Name      Tested ver  Function
========= =========== ==============
pytest     2.6.3       Testing framework
bbfreeze   1.1.3       Extracting stand alone innstalation for Windows
mercurial  3.3         Distributed revision control

Windows Installer XML (WiX) toolset v3.6 (beta) is used to generate windows installer.
