"""
Datasets container
------------------

Dictionary to hold all datasets.
Datasets can be imported or genrated.

"""
# stdlib imports
import logging

# Enthought traits imports
from traits.api import (HasTraits, Dict, Str, Event, Property,
                        on_trait_change, property_depends_on)

# Local imports
from dataset import DataSet


class DatasetCollection(HasTraits):
    """ Application wide collection of datasets

      * _datasets
      * id_name_list
      * name_id_mapping

    Collection of all the data in the application.

    """
    # Dictionary to hold dataset and a editor to select dataset
    _datasets = Dict(Str, DataSet)

    # Events for dataset namechanges
    ds_name_event = Event

    # Events for dictionari content change
    datasets_event = Event

    # Dataset index list
    id_name_list = Property()
    # id_name_list = Property( depends_on = '_datasets' )
    name_id_mapping = Property()

    def get_by_id(self, ds_id):
        """Return DataSet object specified by internal name"""
        return self._datasets[ds_id]

    def id_by_name(self, name):
        return self.name_id_mapping[name]

    def get_by_name(self, name):
        return self.get_by_id(self.id_by_name(name))

    def add_dataset(self, ds):
        """Add or update dataset"""
        name = ds._ds_id
        if self._datasets.__contains__(name):
            raise Exception("Key ({0}) already exists".format(name))
        self._datasets[name] = ds
        self.datasets_event = True
        logging.info("add_dataset: %s", name)

    def delete_dataset(self, ds_id):
        """Remove dataset from collection"""
        del self._datasets[ds_id]
        self.datasets_event = True
        logging.info("delete_dataset: %s", ds_id)

    def get_dataset_list(self):
        return self._datasets.values()


    def get_id_list_by_type(self, ds_type=None):
        if not ds_type:
            return self._datasets.keys()
        ids = []
        for ds in self._datasets.values():
            if ds._dataset_type == ds_type:
                ids.append(ds._ds_id)
        return ids


    @property_depends_on( '_datasets' )
    def _get_id_name_list(self):
        logging.info("Update id_name_list")
        ids = []
        for sn, so in self._datasets.iteritems():
            tu = (sn, so._ds_name)
            ids.append(tu)
        return ids

    # @property_depends_on( '_datasets' )
    def _get_name_id_mapping(self):
        logging.info("Update name_id_mapping")
        id_names = {}
        for si, so in self._datasets.iteritems():
            id_names[so._ds_name] = si
        return id_names

    @on_trait_change('_datasets:_ds_id')
    def _id_change(self, obj, name, old, new):
        """Update dictionary name"""
        moving = self._datasets.pop(old)
        self.add_dataset(moving)
        self.datasets_event = True
        logging.info("dictNameChange: %s change from %s to %s", name, old, new)

    @on_trait_change('_datasets:_dataset_type')
    def _ds_change(self, obj, name, old, new):
        self.datasets_event = True

    @on_trait_change('_datasets:_ds_name')
    def _name_change(self, obj, name, old, new):
        self.ds_name_event = True
        logging.info("displayNameChange: %s changed: %s to %s", name, old, new)


if __name__ == '__main__':
    print("Interactive start")
    def test_print():
        print("Test")
    from tests.conftest import make_dsl_mock
    dsl = make_dsl_mock()
    dsl.on_trait_change(test_print, 'ds_name_event')
    # dsl.print_traits()
