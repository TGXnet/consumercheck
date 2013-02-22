"""A container for all Datasets in the application

"""


# Enthought imports
import traits.api as _traits

# Local imports
from dataset_ng import DataSet, DS_TYPES


class DatasetContainer(_traits.HasTraits):
    """Application wide collection of datasets

    Reccomende API:
     * add(ds1, ds2, ...)
     * get_id_name_map(ds_type_filter=None)
     * self[id]
     * del self[id]
     * event: dsl_changed
     * event: ds_changed
    """

    dsl = _traits.List(DataSet)
    # Fires if datasets is added or removed
    dsl_changed = _traits.Event
    # Fires if a dataset changes its display_name or ds_type
    ds_changed = _traits.Event


    def add(self, ds1, *dsn):
        """Adds one or several datasets to the container
        """
        self.dsl.append(ds1)
        for ds in dsn:
            self.dsl.append(ds)


    def get_id_name_map(self, ds_type_filter=None):
        """Get a lis of tuples with dataset id and names
        """
        if ds_type_filter is not None:
            if ds_type_filter not in DS_TYPES:
                raise ValueError("Not valid dataset type:", ds_type_filter, DS_TYPES)
            else:
                return [(ds.id, ds.display_name)
                        for ds in self.dsl
                        if ds.ds_type == ds_type_filter]
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


    @_traits.on_trait_change('dsl:[display_name,ds_type]')
    def _ds_updated(self, obj, name, old_value, new_value):
        self.ds_changed = True
