
from traits.api import Interface
import traits.has_traits
# 0: no check, 1: warings, 2: error
traits.has_traits.CHECK_INTERFACES = 1

class IDataImporter(Interface):
    """Interface for dataimporting objects"""
    
    def import_data(self, import_settings):
        """Takes an data import settings object and returns a imported dataset"""
