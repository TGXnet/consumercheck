Copyright © 2009-2015 Thomas Graff.


Overview
========

ConsumerCheck is a software for statistical analysis of data from sensory and consumer science, or more precisely data that is acquired from consumer trials and descriptive analysis performed by trained sensory panels. ConsumerCheck has a an easy-to-use graphical user interface that makes the statistical methods available to users that have little or no programming skills.


Installation
============

I wish the answer is:

	pip install consumercheck

But it is not that simple. ConsumerCheck is based on numpy that is not easely automatically installed. Following is a list of the python modules that have to be present for ConsumerCheck to work.

======== =========== ================================================================
 Name     Tested ver  Function
======== =========== ================================================================
chaco     4.4.1       Plotting library -> 4.5.0 (no something goes woring with 4.5.0)
pandas    0.15.1      Matrix container
numpy     1.9.2       Baisis for statistics and datatype
traits    4.5.0       Event and type automation for Traitsui and Chaco
traitsui  4.4.0       Abstract GUI toolkit
pyface    4.4.0       Traitsui nees this
enable    4.4.1       Support for Chaco -> 4.5.0
xlrd      0.9.3       For reading XL spredsheet
openpyxl  1.8.5       For reading XL spredsheet
colormath 2.1.0       Latest version
pyper     1.1.1       Python <-> R communication

If you are on Window or OS X the easiest you can do is to install the `Anaconda <http://continuum.io/downloads>`_ python environment from Continiuum Analytic. If you are on one of the UNIX platforms I imagien you are savy enought to not require any hand-holding.

In addition ConsumerCheck uses the `R <https://www.r-project.org/>`_ environment for statistical computing. So this have to be installed on you system for ConsumerCheck to function properly. There also have to be installed som libraries in the R environment:

	lmerTest	ver 2.0-11


Latest changes
==============

Nothing here yet.


Roadmap
=======

Nothing here yet.
