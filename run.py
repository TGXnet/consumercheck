# coding=utf-8

# Local imports
from dataset_collection import DatasetCollection
from dataset import DataSet
from datasets_ui import DatasetsView


def main():
    """Run the application. """

    sets = DatasetCollection()
    view = DatasetsView()
    view.configure_traits()



if __name__ == '__main__':
    main()

#### EOF ######################################################################
