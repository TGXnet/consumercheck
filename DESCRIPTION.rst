Copyright © 2009-2015 Thomas Graff.


Overview
========

ConsumerCheck is a software for statistical analysis of data from sensory and consumer science, or more precisely data that is acquired from consumer trials and descriptive analysis performed by trained sensory panels. ConsumerCheck has a an easy-to-use graphical user interface that makes the statistical methods available to users that have little or no programming skills.


Installation
============

I wish the answer was:

	pip install consumercheck

But unfortunately it is not that simple. The following list of python modules needs to be installed prior to using **pip install consumercheck** in order to make ConsumerCheck work.

+-------------+------------+-----------------------------------------------------------------+
| Name        | Tested ver | Function                                                        |
+=============+============+=================================================================+
|chaco        | 4.4.1      | Plotting library                                                |
+-------------+------------+-----------------------------------------------------------------+
|pandas       | 0.15.1     | Matrix container (0.16.2)                                       |
+-------------+------------+-----------------------------------------------------------------+
|numpy        | 1.9.2      | Basis for statistics and datatype                               |
+-------------+------------+-----------------------------------------------------------------+
|traits       | 4.5.0      | Event and type automation for Traitsui and Chaco                |
+-------------+------------+-----------------------------------------------------------------+
|traitsui     | 4.4.0      | Abstract GUI toolkit                                            |
+-------------+------------+-----------------------------------------------------------------+
|pyface       | 4.4.0      | Traitsui needs this                                             |
+-------------+------------+-----------------------------------------------------------------+
|enable       | 4.4.1      | Support for Chaco                                               |
+-------------+------------+-----------------------------------------------------------------+
|xlrd         | 0.9.3      | For reading XL spreadsheet                                      |
+-------------+------------+-----------------------------------------------------------------+
|openpyxl     | 1.8.5      | For reading XL spreadsheet                                      |
+-------------+------------+-----------------------------------------------------------------+
|colormath    | 2.1.1      | Latest version                                                  |
+-------------+------------+-----------------------------------------------------------------+
|pyper        | 1.1.1      | Python <-> R communication                                      |
+-------------+------------+-----------------------------------------------------------------+
|configparser | 3.3.0      | Parsing configfile                                              |
+-------------+------------+-----------------------------------------------------------------+

Moreover, ConsumerCheck uses the `R <https://www.r-project.org/>`_ environment for statistical computing. This means you need to have R (> 3.0) installed on your platform. Furthermore, the following R-package needs to be installed:

	lmerTest	ver 2.0-11


MS Windows and Mac OS X
-----------------------

If you are on MS Window or Mac OS X the easiest way is to install the required Python packages listed above by installing the `Anaconda <http://continuum.io/downloads>`_ python environment from Continuum Analytics.

Then you have to use the Conda installer to add some additional python packages that are needed for ConsumerCheck. In a Windows PowerShell / Mac terminal type:

	conda install chaco


After this, ConsumerCheck can be installed with pip:

	pip install consumercheck


Linux
-----

The following installation procecure was tested on Debian Jessie 8.2.

On the shell commandline::

  sudo apt-get --no-install-recommends install python-pip python-pandas python-chaco python-qt4-gl python-networkx python-configparser r-base r-cran-lme4 r-cran-numderiv r-cran-hmisc r-cran-gplots r-cran-nloptr r-cran-plyr r-cran-ggplot2

  sudo pip install consumercheck


Then you have to start R and run the following commands::

  install.packages(c("pbkrtest"))
  pkgurl <- "http://cran.r-project.org/src/contrib/Archive/lmerTest/lmerTest_2.0-11.tar.gz"
  install.packages(pkgurl, repos=NULL, type="source")


Running ConsumerCheck
---------------------

ConsumerCheck is started by typing **ccgui** on the command line.


Latest changes
==============

Nothing here yet.


Roadmap
=======

Nothing here yet.
