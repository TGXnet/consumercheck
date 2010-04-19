# coding=utf-8

# Enthought imports
from enthought.traits.api \
    import HasTraits, File, Bool
from enthought.traits.ui.api \
    import View, Item, Group, FileEditor, ButtonEditor


class FileImport(HasTraits):
    """File import dialog"""
    fileName = File()
    colHead = Bool(True)
    txtObjNames = Bool(False)
