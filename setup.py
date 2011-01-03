# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 15:02:41 2010

@author: Thomas Graff
"""

from distutils.core import setup
#from glob import glob
#import os
import py2exe

#msvc_files = [("Microsoft.VC90.CRT", glob(r'c:\dev\ms-vc-runtime\*.*'))]

excludes = ["pywin", "pywin.debugger", "pywin.debugger.dbgcon",
			"pywin.dialogs", "pywin.dialogs.list",
			"Tkconstants","Tkinter","tcl",
			"encodings"
			]


includes = ["encodings",
			"encodings.latin_1",]


options = {"py2exe": {
	"compressed": 1,
	"optimize": 2,
	"excludes": excludes,
	"includes": includes,
}}


setup(windows = ['run.py'],
	options = options,
	name = 'ConsumerCheck',
	version = '0.5',
	author = 'Thomas Graff',
	author_email = 'graff.thomas@google.com',
	url='http://www.tgxnet.no/',
	download_url = 'http://www.tgxnet.no/',
	maintainer = 'Oliver Tomic',
	maintainer_email = 'oiver@matforsk.no',
	description = 'Nofima Software',
	long_description = 'Statistical analysis',
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: Python Software Foundation License',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX',
		'Programming Language :: Python',
		'Topic :: Software Development :: Bug Tracking',
		],
	platforms = '',
	license = 'Whatever',
#	 packages=['distutils', 'distutils.command'],
#	 py_modules = ['foo'],
#	 data_files = [('datapakker', ['datapakker/kilde/datatull.org'])],
#	 py_modules = ['rpy-locate'],
	)
