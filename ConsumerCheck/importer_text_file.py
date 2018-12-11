'''ConsumerCheck
'''
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------

# StdLib imports
import logging
logger = logging.getLogger('tgxnet.nofima.cc.'+__name__)

# SciPy imports
import numpy as _np
import pandas as _pd

# Enthought imports
import traits.api as _tr
import traitsui.api as _tui
from traitsui.menu import OKButton, CancelButton
from traitsui.tabular_adapter import TabularAdapter


# Local imports
from dataset import DataSet, SubSet, VisualStyle
from importer_interfaces import IDataImporter
from importer_file_base import ImporterFileBase
from utilities import from_palette



class RawLineAdapter(TabularAdapter):
    ncols = _tr.Int()
    # Temporary column to avoid crash
    columns = ['tmp']
    width = 70


    def _ncols_changed(self, info):
        self.columns = [("col{}".format(i), i) for i in range(self.ncols)]


class PreviewTableEditor(_tui.TabularEditor):
    update_cells = _tr.Event()


preview_table = PreviewTableEditor(
    adapter=RawLineAdapter(),
    operations=[],
    show_titles=True,
    editable=False,
    update='update_cells',
)


class FilePreviewer(_tui.Handler):
    _raw_lines = _tr.List(_tr.Str)
    _unicode_lines = _tr.List(_tr.Unicode)
    _parsed_data = _tr.List()


    def init(self, info):
        self._probe_read(info.object)
        self._decode_chars(info.object.char_encoding)


    def object_have_var_names_changed(self, info):
        preview_table.update_cells = True


    def object_delimiter_changed(self, info):
        self._split_table(info.object.delimiter)


    def _split_table(self, delimiter):
        preview_matrix = [line.split(delimiter) for line in self._unicode_lines]
        max_cols = 7
        for row in preview_matrix:
            max_cols = min(max_cols, len(row))
        self._parsed_data = self._fix_preview_matrix(preview_matrix, max_cols)
        preview_table.adapter.ncols = max_cols


    def object_char_encoding_changed(self, info):
        self._decode_chars(info.object.char_encoding)
        self._split_table(info.object.delimiter)


    def _decode_chars(self, encoding):
        self._unicode_lines = [line.decode(encoding, errors='replace') for line in self._raw_lines]


    def _fix_preview_matrix(self, preview_matrix, length):
        for i, row in enumerate(preview_matrix):
            if len(row) < length:
                preview_matrix[i] += ['']*(length-len(row))
            elif len(row) > length:
                preview_matrix[i] = preview_matrix[i][0:length]

        return preview_matrix


    def _probe_read(self, obj, n_lines=100, length=200):
        lines = []
        with open(obj.file_path, 'rU') as fp:
            for i in range(n_lines):
                line = fp.readline(length)
                if not line:
                    break
                if not ('\r' in line or '\n' in line):
                    fp.readline()
                logger.debug("linje {}: {}".format(i, line.rstrip('\n')))
                lines.append(line.rstrip('\n'))
        self._raw_lines = lines


preview_handler = FilePreviewer()



class ImporterTextFile(ImporterFileBase):
    _tr.implements(IDataImporter)

    delimiter = _tr.Enum('\t', ',', ' ', ';')
    decimal_mark = _tr.Enum('period', 'comma')
    char_encoding = _tr.Str('utf_8')


    def import_data(self):
        """Do the importing of a data set"""

        if self.have_var_names:
            header = 'infer'
        else:
            header = None
        if self.have_obj_names:
            index_col = 0
        else:
            index_col = None

        dsdf = _pd.read_csv(
            filepath_or_buffer=self.file_path,
            delimiter=self.delimiter,
            header=header,
            index_col=index_col,
            keep_default_na=True,
            na_values=['?'],
            encoding=self.char_encoding,
        )

        # FIXME: This is hackish
        # I have to know the matrix shape to use converters
        if self.decimal_mark == 'comma':

            def c2f(a_num):
                '''Alfanumeric with comma to float'''
                return float(a_num.replace(',', '.'))

            convs = {k: c2f for k in dsdf.columns}

            dsdf = _pd.read_csv(
                filepath_or_buffer=self.file_path,
                delimiter=self.delimiter,
                header=header,
                index_col=index_col,
                keep_default_na=True,
                na_values=['?'],
                encoding=self.char_encoding,
                converters=convs,
            )


        if not self.have_var_names:
            dsdf.columns = ["V{0}".format(i+1) for i in range(dsdf.shape[1])]
        if not self.have_obj_names:
            dsdf.index = ["O{0}".format(i+1) for i in range(dsdf.shape[0])]

        # Check if we hav a column with class information
        grouping_names = [cn for cn in dsdf.columns if cn[0] == '_']
        groupings = [(gn, set(dsdf.loc[:,gn])) for gn in grouping_names]

        # List with index names
        # auto_colors = ["green", "lightgreen",
        #                "blue", "lightblue",
        #                "red", "pink",
        #                "darkgray", "silver"]

        subsets_groups = {}
        # grouping_name, classes_group
        for gn, cg in groupings:
            # subsets_group
            ssg = []
            for idx, cid in enumerate(cg):
                ss = SubSet(id=str(cid), name='Class {}'.format(cid))
                # ss.gr_style = VisualStyle(fg_color=auto_colors[idx % 8])
                ss.gr_style = VisualStyle(fg_color=from_palette())
                ss.row_selector = list(dsdf[dsdf.loc[:,gn] == cid].index)
                ssg.append(ss)
            ngn = gn[1:]
            subsets_groups[ngn] = ssg
            dsdf.drop(gn, axis=1, inplace=True)

        # Make DataSet
        ds = DataSet(
            mat=dsdf,
            display_name=self.ds_name,
            kind=self.kind,
            subs=subsets_groups,
        )
        return ds


    traits_view = _tui.View(
        _tui.Group(
            _tui.Item('file_path', style='readonly'),
            _tui.Item('handler._parsed_data',
                      editor=preview_table,
                      id='table',
                      show_label=False),
            _tui.Item('delimiter',
                      editor=_tui.EnumEditor(
                          values={
                              '\t': '1:Tab',
                              ',': '2:Comma (,)',
                              ' ': '3:Space',
                              ';': '4:Semicolon (;)',
                          }),
                      style='custom'),
            _tui.Item('decimal_mark'),
            _tui.Item('ds_name', label='Data set name'),
            _tui.Item('kind', editor=_tui.EnumEditor(name='kind_list'), label='Data set type'),
            _tui.Item('have_var_names', label='Existing variable names',
                      tooltip='Is first row variable names?'),
            _tui.Item('have_obj_names', label='Existing object names',
                      tooltip='Is first column object names?'),
            show_labels=True,
        ),
        title='Raw data preview',
        width=0.45,
        height=0.6,
        resizable=True,
        buttons=[CancelButton, OKButton],
        handler=preview_handler,
        kind='livemodal',
    )


# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    import os
    import sys
    dpath = os.environ['CC_TESTDATA']
    dfile = dpath + '/Iris/iris_multiclass.csv'
    # dfile = dpath + '/Iris/irisNoClass.data'
    itf = ImporterTextFile(
        file_path=dfile,
        delimiter=',',
        have_obj_names=False
    )
    # itf.configure_traits()
    ds = itf.import_data()
    print(ds.mat.shape)
    print(ds.mat.head())
    print(ds.get_subset_groups())
