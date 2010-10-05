# -*- coding: utf-8 -*-

from bbfreeze import Freezer

frezer = Freezer(
    "dist_bbfreeze",
    includes=("_strptime",),
    excludes=(),
    )
frezer.addScript("run.py")
frezer()    # starts the freezing process
