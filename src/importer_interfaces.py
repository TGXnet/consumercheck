
from traits.api import Interface, Bool, Enum, File, Str


class IDataImporter(Interface):
    """Interface for dataimporting objects."""

    file_path = File()
    """Path to the file to be imported."""

    transpose = Bool(False)
    """Should the data be transposed during import."""

    have_var_names = Bool(True)
    """Does the data have variable names?"""

    have_obj_names = Bool(True)
    """Does the data have object names?"""

    ds_id = Str()
    """An internal (not shown to the user) name for the dataset."""

    ds_name = Str()
    """An userfriendly name for the dataset."""

    ds_type = Enum(
        ('Design variable',
         'Sensory profiling',
         'Consumer liking',
         'Consumer attributes',)
        )
    """The dataset type for this dataset."""

    def import_data(self):
        """Takes an data import settings object and returns a imported dataset"""

    ## def configure_traits(self):
    ##     """Show dialog for configuring data import"""
