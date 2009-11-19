# coding=utf-8

# Local imports
from dataset_collection import DatasetCollection
from dataset import DataSet
from datasets_ui import DatasetsView


def main():
    """Run the application. """
    # Add test setst to collection
    firstDataset = DataSet()
    firstDataset._internalName = 'gurg1'
    firstDataset._displayName = 'Test set one'
    secondDataset = DataSet()
    secondDataset._internalName = 'gug2re'
    secondDataset._displayName = 'Second test set'
    sets = DatasetCollection()
    sets.addDataset(firstDataset)
    sets.addDataset(secondDataset)

    view = DatasetsView(vc=sets, vs=secondDataset)
    view.configure_traits()



if __name__ == '__main__':
    main()

#### EOF ######################################################################
