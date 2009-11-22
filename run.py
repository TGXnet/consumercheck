# coding=utf-8

# Enthought imports
from enthought.pyface.api import GUI

# Local imports
from dataset_collection import DatasetCollection
from dataset import DataSet
from datasets_ui import DatasetsView

def main():
    """Run the application. """
    # Add test setst to collection
    sets = DatasetCollection()
    view = DatasetsView(vc=sets)
    view.edit_traits()
    GUI().start_event_loop()



if __name__ == '__main__':
    main()

#### EOF ######################################################################
