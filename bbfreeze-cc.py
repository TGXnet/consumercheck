from bbfreeze import Freezer

includes = ('')
exclude3 = ('pydoc', 'pydoc_topics', 'pkg_resources', 'doctest', 'difflib',
            'cookielib', 'urllib', 'urllib2' 'acb', 'anydbm', 'ast', 'base64',
            'pstats', 'TiffImagePlugin', 'uuid', 'modulefinder', 'xml', 'PIL')
excludes = ('pydoc', 'pydoc_topics', 'doctest',
            'TiffImagePlugin', 'modulefinder', 'xml', 'PIL')

freeze = Freezer("consumercheck-0.4.1", includes=includes, excludes=excludes)
freeze.addScript("consumercheck.py", gui_only=True)
freeze.use_compression = 0
freeze.include_py = True
freeze()    # starts the freezing process
