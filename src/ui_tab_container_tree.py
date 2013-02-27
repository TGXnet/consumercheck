
import traits.api as _traits
import traitsui.api as _traitsui

from dataset_ng import DataSet
from dataset_container import DatasetContainer


class DSNode(_traitsui.TreeNode):

    def get_icon(self, obj, is_expanded):
        """Return icon name based on ds type
        """
        if obj.ds_type == 'Design variable':
            return 'design_variable.ico'
        elif obj.ds_type == 'Sensory profiling':
            return 'sensory_profiling.ico'
        else:
            return 'customer_liking.ico'


class DSHandler(_traitsui.Handler):
    summary = _traits.Str()

    def init(self, info):
        mtx = info.object.mat
        self.summary = ''
        rows, cols = mtx.shape
        vals = rows * cols
        notnan = mtx.count().sum()
        nans = vals - notnan
        vmax = mtx.max().max()
        vmin = mtx.min().min()
        vmean = mtx.mean().mean()
        vstd = mtx.std().std()
        self.summary += "{k1:6s}:{v1:4.3g}\t{k2:6s}:{v2:4.3g}\n".format(
            k1='Rows', v1=rows, k2='Cols', v2=cols)
        self.summary += "{k1:6s}:{v1:4.3g}\t{k2:6s}:{v2:4.3g}\n".format(
            k1='Missing', v1=nans, k2='Total', v2=vals)
        self.summary += "{k1:6s}:{v1:4.3g}\t{k2:6s}:{v2:4.3g}\n".format(
            k1='Min', v1=vmin, k2='Max', v2=vmax)
        self.summary += "{k1:6s}:{v1:4.3g}\t{k2:6s}:{v2:4.3g}\n".format(
            k1='Mean', v1=vmean, k2='STD', v2=vstd)


ds_view = _traitsui.View(

    _traitsui.Group(
        _traitsui.Group(
            _traitsui.Item('id', style='readonly'),
            _traitsui.Label('Dataset name:'),
            _traitsui.Item('display_name', show_label=False),
            _traitsui.Label('Dataset type:'),
            _traitsui.Item('ds_type', show_label=False),
            ),
        _traitsui.Group(
            _traitsui.Item('handler.summary', style='readonly', show_label=False),
            label='Dataset summary',
            show_border=True,
            ),
        ),
    kind='nonmodal',
    handler=DSHandler(),
    )


list_view = _traitsui.View(
    _traitsui.Heading('List showing all imported datasets'),
    width=500,
    )


tree_editor = _traitsui.TreeEditor(
    nodes = [
        _traitsui.TreeNode(
            node_for=[DatasetContainer],
            label='=Datasets',
            children='dsl',
            view=list_view,
            ),
        DSNode(
            node_for=[DataSet],
            label='display_name',
            tooltip='ds_type',
            icon_path = 'graphics',
            view=ds_view,
            ),
        ],
    refresh='object.tulle_event',
    ## editable=False,
    alternating_row_colors=True,
    )
