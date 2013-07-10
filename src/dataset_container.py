"""A container for all Datasets in the application

"""


# Enthought imports
import traits.api as _traits

# Local imports
from dataset import DataSet, DS_TYPES


class DatasetContainer(_traits.HasTraits):
    """Application wide collection of datasets

    Reccomende API:
     * add(ds1, ds2, ...)
     * get_id_name_map(kind_filter=None)
     * self[id]
     * del self[id]
     * event: dsl_changed
     * event: ds_changed
    """

    dsl = _traits.List(DataSet)
    # Fires if datasets is added or removed
    dsl_changed = _traits.Event
    # Fires if a dataset changes its display_name or kind
    ds_changed = _traits.Event


    def add(self, ds1, *dsn):
        """Adds one or several datasets to the container
        """
        self.dsl.append(ds1)
        for ds in dsn:
            self.dsl.append(ds)


    def get_id_name_map(self, kind_filter=None, kind_exclude=None):
        """Get a lis of tuples with dataset id and names
        """
        if kind_filter is not None:
            if kind_filter not in DS_TYPES:
                raise ValueError("Not valid dataset type:", kind_filter, DS_TYPES)
            else:
                return [(ds.id, ds.display_name)
                        for ds in self.dsl
                        if ds.kind == kind_filter]
        if kind_exclude is not None:
            if kind_exclude not in DS_TYPES:
                raise ValueError("Not valid dataset type:", kind_exclude, DS_TYPES)
            else:
                return [(ds.id, ds.display_name)
                        for ds in self.dsl
                        if ds.kind != kind_exclude]
        else:
            return [(ds.id, ds.display_name)
                    for ds in self.dsl]


    def __len__(self):
        return len(self.dsl)


    def __getitem__(self, key):
        # may raise TypeError
        idx = self.dsl.index(key)
        return self.dsl[idx]


    def __delitem__(self, key):
        idx = self.dsl.index(key)
        del self.dsl[idx]


    @_traits.on_trait_change('dsl[]')
    def _dsl_updated(self, obj, name, old_value, new_value):
        self.dsl_changed = True


    @_traits.on_trait_change('dsl:[display_name,kind]')
    def _ds_updated(self, obj, name, old_value, new_value):
        self.ds_changed = True



def get_ds_by_name(name, dsc):
    '''Utility function if you realy want to get dataset by name.

    This is not encouraged because several datasets can have same name,
    and be differentiated by other traits like dimensions, dataset type,
    style metadata o.l.
    '''
    nid = dict([(m[1], m[0]) for m in dsc.get_id_name_map()])
    return dsc[nid[name]]
