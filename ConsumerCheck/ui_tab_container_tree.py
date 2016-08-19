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


from traits.etsconfig.api import ETSConfig
import traits.api as _traits
import traitsui.api as _traitsui

if ETSConfig.toolkit == 'wx':
    import traitsui.wx.tree_editor as _te
elif ETSConfig.toolkit == 'qt4':
    import traitsui.qt4.tree_editor as _te

from dataset import DataSet
from dataset_container import DatasetContainer
from ds_table_view import DSTableViewer


win_handle = None


class DSNode(_traitsui.TreeNode):
    '''Cusom tree node for data sets.

    Sets tree node icon based on data set type
    '''
    def get_icon(self, obj, is_expanded):
        """Return icon name based on ds type
        """
        if obj.kind == 'Product design':
            return 'design_variable.ico'
        elif obj.kind == 'Descriptive analysis / sensory profiling':
            return 'sensory_profiling.ico'
        elif obj.kind == 'Consumer liking':
            return 'customer_liking.ico'
        elif obj.kind == 'Consumer characteristics':
            return 'customer_attributes.ico'
        else:
            return self.icon_item


class DSHandler(_traitsui.Handler):
    summary = _traits.Str()

    def init(self, info):
        super(DSHandler, self).init(info)
        # FIXME: There must be a better way
        global win_handle
        win_handle = info.ui.control
        mtx = info.object.mat
        self.summary = ''
        rows, cols = mtx.shape
        vals = rows * cols
        notnan = mtx.count().sum()
        nans = vals - notnan
        vmax = mtx.values.max()
        vmin = mtx.values.min()
        vmean = mtx.values.mean()
        vstd = mtx.values.std()
        self.summary += "{k1:6s}:{v1:4.3g}\t{k2:6s}:{v2:4.3g}\n".format(
            k1='Rows', v1=rows, k2='Cols', v2=cols)
        self.summary += "{k1:6s}:{v1:4.3g}\t{k2:6s}:{v2:4.3g}\n".format(
            k1='Missing', v1=nans, k2='Total', v2=vals)
        self.summary += "{k1:6s}:{v1:4.3g}\t{k2:6s}:{v2:4.3g}\n".format(
            k1='Min', v1=vmin, k2='Max', v2=vmax)
        self.summary += "{k1:6s}:{v1:4.3g}\t{k2:6s}:{v2:4.3g}\n".format(
            k1='Mean', v1=vmean, k2='STD', v2=vstd)


transpose_action = _traitsui.Action(
    name='Create transposed copy',
    action='handler.transpose_ds(editor, object)')


tr_menu = _traitsui.Menu(
    transpose_action,
    _te.DeleteAction)


ds_view = _traitsui.View(

    _traitsui.Group(
        _traitsui.Group(
            _traitsui.Item('id', style='readonly'),
            _traitsui.Label('Data set name:'),
            _traitsui.Item('display_name', show_label=False),
            _traitsui.Label('Data set type:'),
            _traitsui.Item('kind', show_label=False),
            ),
        _traitsui.Group(
            _traitsui.Item('handler.summary', style='readonly', show_label=False),
            label='Data set summary',
            show_border=True,
            ),
        ),
    kind='nonmodal',
    handler=DSHandler(),
    )


list_view = _traitsui.View(
    _traitsui.Heading('List showing all imported data sets'),
    width=500,
    )


def dclk_activator(obj):
    dstv = DSTableViewer(obj)
    dstv.edit_traits(view=dstv.get_view(), parent=win_handle)


tree_editor = _traitsui.TreeEditor(
    nodes = [
        _traitsui.TreeNode(
            node_for=[DatasetContainer],
            label='=Data sets',
            children='',
            auto_open=True,
            view=list_view,
            ),
        _traitsui.TreeNode(
            node_for=[DatasetContainer],
            label='=Data sets',
            children='dsl',
            auto_open=True,
            view=list_view,
            ),
        DSNode(
            node_for=[DataSet],
            label='display_name',
            tooltip='kind',
            icon_path='graphics',
            on_dclick=dclk_activator,
            menu=tr_menu,
            view=ds_view,
            ),
        ],
    ## refresh='object.tulle_event',
    ## editable=False,
    hide_root=True,
    alternating_row_colors=True,
    )
