
=================
 Coding standard
=================

Coding style
============

Inspiration and guideline

`Style Guide for Python Code <http://www.python.org/dev/peps/pep-0008/>`_
`Google Python Style Guide <http://google-styleguide.googlecode.com/svn/trunk/pyguide.html>`_


Checking tools
--------------

Tools for enforcing style and consistency:
 * pyflakes
 * pylint
 * pychecker

http://www.logilab.org/card/pylint_tutorial


Documentatio
============

Balance list:
 #. Write relevant info in source files and general info in tematic files.
 #. In source file balance syntax for pydoc and Sphinx.
 #. Minimize unnesseary documentation.

`Docstring Conventions <http://www.python.org/dev/peps/pep-0257/>`_
`Documenting Your Project Using Sphinx <http://packages.python.org/an_example_pypi_project/sphinx.html>`_
`Restructured Text (reST) and Sphinx CheatSheet <http://openalea.gforge.inria.fr/doc/openalea/doc/_build/html/source/sphinx/rest_syntax.html>`_

`Matplotlib sampledoc tutorial <http://matplotlib.sourceforge.net/sampledoc/index.html>`_
`Conventions for Coding in Sage <http://www.sagemath.org/doc/developer/conventions.html>`_


Testing and quality control
===========================

Mainly use py.test.


Release management
==================

Procedure:
 #. Release management
 #. mercurial verion tag
 #. track version tag for tickets
 #. update version info in about_consumercheck
 #. update freeze script
 #. update pacakge build script


Feedback and bugfixing
======================

Trac and mail for error report and feature request.
