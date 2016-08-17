'''Reading and import of data sets.

Read a file and make a data set object.

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

# Std lib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)
import os.path

# SciPy imports
import numpy as _np

# Enthought imports
from traits.api import HasTraits, Bool, File, List, Str
from traitsui.api import View, Item
from traitsui.menu import OKButton
from pyface.api import FileDialog, OK, CANCEL, warning

# Local imports
import cc_config as conf
from importer_text_file import ImporterTextFile
from importer_xls_file import ImporterXlsFile
# from importer_xlsx_file import ImporterXlsxFile

__all__ = ['ImporterMain']


class ImporterMain(HasTraits):
    """Importer class"""

    _last_open_path = File()
    _files_path = List(File)
    _notice_shown = Bool(False)


    def import_data(self, file_path, have_variable_names = True, have_object_names = True, sep='\t'):
        """Read file and return DataSet objekt

        Does not show any UI.
        """
        importer = self._make_importer(file_path)
        importer.have_var_names = have_variable_names
        importer.have_obj_names = have_object_names
        importer.delimiter = sep
        ds = importer.import_data()
        return ds


    def dnd_import_data(self, path):
        """Drag and drop reactor

        Open dialog for dragged file, import and return the DataSet
        """
        importer = self._make_importer(path)
        importer.edit_traits()
        ds = importer.import_data()
        return ds


    def dialog_multi_import(self, parent_window=None):
        """Multi file import

        Open dialog for selecting multiple files.
        Shows a settings dialog for each selected file
        return a list of imported DataSet's
        """
        self._last_open_path = conf.get_option('work_dir')
        logger.debug('Last imported file: %s', self._last_open_path)

        # Show info about legal data format
        if not self._notice_shown:
            notice = ImportNotice()
            notice.edit_traits()
            self._notice_shown = True

        # Select files
        status = self._show_file_selector()
        if status == CANCEL:
            logger.info('Cancel file imports')
            return []
        datasets = []
        logger.debug('File(s) to import: \n%s', '\n'.join(self._files_path))

        for file_n in self._files_path:
            importer = self._make_importer(file_n)
            logger.info('Attempting to import %s with %s', file_n, type(importer))
            ui = importer.edit_traits()
            if ui.result:
                ds = importer.import_data()
                if ds.values.dtype.type is _np.object_:
                    logger.warning('Importing matrix with non-numeric values: {}'.format(ds.display_name))
                    if parent_window is not None:
                        warning(parent_window, 'This matrix contains non-numeric values. The statistical methods is not able to handle non-numeric categorical variables')
                datasets.append(ds)
            else:
                continue
        conf.set_option('work_dir', file_n)
        return datasets


    # For select multi file dialog
    def _show_file_selector(self):
        dlg = FileDialog(
            action='open files',
            default_path=self._last_open_path,
            title='Import data')
        status = dlg.open()
        if status == OK:
            self._files_path = dlg.paths
        elif status == CANCEL:
            pass
        return status


    def _make_importer(self, path):
        fext = self._identify_filetype(path)
        if fext in ['txt', 'csv']:
            return ImporterTextFile(file_path=path)
        elif fext in ['xls', 'xlsx', 'xlsm']:
            return ImporterXlsFile(file_path=path)
        else:
            return ImporterTextFile(file_path=path)


    def _identify_filetype(self, path):
        fn = os.path.basename(path)
        return fn.partition('.')[2].lower()


class ImportNotice(HasTraits):
    message = Str('''
This summary provides information on the import of data into ConsumerCheck.


--------------
Data structure
--------------
The following data structure is required for successful import:

the data needs to be organised in typical two-way data matrices with rows and columns
the data may or may not contain column names and row names 
the data should be separated by either comma, space or semicolon
Only numerical values are allowed in the data (example: numbers should be used to indicate levels of design variables, consumer characteristics, etc.)
ConsumerCheck doesn't handle non-English characters in the row and column names


--------------
Data type tags
--------------

For improved usability and handling of the data within ConsumerCheck, each data should get a tag that indicates the type of data. Note that adding a tag is not mandatory, but may simplify use of the statistical methods in ConsumerCheck. The following tags are available:

1. Tag for "Descriptive analysis/sensory profiling" data where:
rows represent products 
columns represent sensory attributes

2. Tag for "Consumer liking" data where:
rows represent products
columns represent consumers

3. Tag for "Consumer characteristics" data where:
rows represent consumers
columns represent characteristics

4. Tag for "Product design" data where: 
rows represent products
columns represent design variables

5. Tag for "Other" data where:
	rows and columns represent data that is not suitable for any of the tags in 1 to 4 


Example:
With the analysis method "preference mapping", only data tagged "Descriptive analysis/sensory profiling" and "Consumer liking" will be available for selection.
With the analysis method "conjoint analysis", only data tagged "Consumer liking", "Consumer characteristics" and "Product design" will be available for selection.


-----------------
Import from Excel
-----------------

Excel files and sheets may contain cells that store information that is invisible to the user. This may lead to various import errors when trying to import from such Excel files. If you experience problems when reading data from Excel, you may do the following to remedy the problem: 

- mark only data you wish to import; copy and paste the data into a new Excel file sheet and try import from this new Excel file.


----------------------------------------
Defining categories for rows and columns
----------------------------------------

If you wish to introduce categories to you data, you may do so by adding category rows and/or category columns to your data matrix. 

Categories representing rows (products):
Add columns where the column name starts with an underscore (examples for a category column names: "_fatContent", "_brand", etc.). In the category column, provide a category ID for each row. By doing so, each row category will be represented by its own colour in the respective plots.

Categories representing columns (variables such as sensory attributes, consumer characteristics, etx):
Add rows where the row name starts with an underscore (examples for a category row names: "_sex", "_income", etc.). In the category row, provide a category ID for each column. By doing so, each column category will be represented by its own colour in the respective plots.
'''
        )

    traits_view = View(
        Item('message', show_label=False, springy=True, style='custom' ),
        title='Data import summary',
        height=300,
        width=600,
        resizable=True,
        buttons=[OKButton],
        kind='modal',
        )


#Instantiate DND
DND = ImporterMain()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    fi = ImporterMain()
    dsc = fi.dialog_multi_import()
    for ds in dsc:
        ds.print_traits()
        print(ds.mat.dtypes)
