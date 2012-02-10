
from traits.api import Interface


class IDataImporter(Interface):
    """Interface for dataimporting objects"""
    
    def import_data(self):
        """Takes an data import settings object and returns a imported dataset"""

    def configure_traits(self):
        """Show dialog for configuring data import"""
        
