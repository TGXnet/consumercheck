
from traits.api import Interface
import traits.has_traits
# 0: no check, 1: warings, 2: error
traits.has_traits.CHECK_INTERFACES = 1

class IDataImporter(Interface):
    """Interface for dataimporting objects"""
    
    def import_data(self):
        """Takes an data import settings object and returns a imported dataset"""

    def configure_traits(self):
        """Show dialog for configuring data import"""
        