"""Datasets container

Dictionary to hold all datasets.
Datasets can be imported or genrated.

"""
# stdlib imports
import logging

# Enthought traits imports
from enthought.traits.api import HasTraits, Dict, Str, Event, Property, \
     on_trait_change, property_depends_on

# Local imports
from dataset import DataSet

class DatasetCollection(HasTraits):
    """ Application wide collection of datasets

    Members
    =======
      * dataDict
      * indexNameList

    Description
    ===========
    Collection of all the data in the application.

    """
    # Dictionary to hold dataset and a editor to select dataset
    _datasets = Dict(Str, DataSet)

    # Events for dataset namechanges
    datasetNameChanged = Event

    # Events for dictionari content change
    dataDictContentChanged = Event

    # Dataset index list
    indexNameList = Property()
    # indexNameList = Property( depends_on = '_datasets' )
    nameMap = Property()

    def get_by_id(self, ds_id):
        """Return DataSet object specified by internal name"""
        return self._datasets[ds_id]

    def id_by_name(self, name):
        return self.nameMap[name]

    def get_by_name(self, name):
        return self.get_by_id(self.id_by_name(name))

    def add_dataset(self, ds):
        """Add or update dataset"""
        name = ds._ds_id
        if self._datasets.__contains__(name):
            raise Exception("Key ({0}) already exists".format(name))
        self._datasets[name] = ds
        self.dataDictContentChanged = True
        logging.info("add_dataset: %s", name)

    def delete_dataset(self, ds_id):
        """Remove dataset from collection"""
        del self._datasets[ds_id]
        self.dataDictContentChanged = True
        logging.info("delete_dataset: %s", ds_id)

    def get_dataset_list(self):
        return self._datasets.values()

    @property_depends_on( '_datasets' )
    def _get_id_list(self):
        logging.info("Update indexNameList")
        ids = []
        for sn, so in self._datasets.iteritems():
            tu = (sn, so._ds_name)
            ids.append(tu)
        return ids

    # @property_depends_on( '_datasets' )
    def _get_id_name(self):
        logging.info("Update nameMap")
        id_names = {}
        for si, so in self._datasets.iteritems():
            id_names[so._ds_name] = si
        return id_names

    @on_trait_change('_datasets:_ds_id')
    def _id_change(self, obj, name, old, new):
        """Update dictionary name"""
        moving = self._datasets.pop(old)
        self.add_dataset(moving)
        self.dataDictContentChanged = True
        logging.info("dictNameChange: %s change from %s to %s", name, old, new)

    @on_trait_change('_datasets:_ds_name')
    def _name_change(self, obj, name, old, new):
        self.datasetNameChanged = True
        logging.info("displayNameChange: %s changed: %s to %s", name, old, new)


if __name__ == '__main__':
    print("Interactive start")
    from tests.tools import make_dsl_mock
    dsl = make_dsl_mock()
