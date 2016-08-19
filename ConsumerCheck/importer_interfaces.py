'''ConsumerCheck
'''
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 Thomas Graff <thomas.graff@tgxnet.no>
#
#  This file is part of ConsumerCheck.
#
#  ConsumerCheck is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  ConsumerCheck is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ConsumerCheck.  If not, see <http://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------

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
    """An internal (not shown to the user) name for the data set."""

    ds_name = Str()
    """An userfriendly name for the data set."""

    kind = Enum(
        ('Product design',
         'Descriptive analysis / sensory profiling',
         'Consumer liking',
         'Consumer characteristics',)
    )
    """The data set type for this data set."""

    def import_data(self):
        """Takes an data import settings object and returns a imported data set"""

    ## def configure_traits(self):
    ##     """Show dialog for configuring data import"""
