# coding=utf-8

# Enthought imports
from enthought.pyface.api import GUI

# Local imports
from dataset_collection import DatasetCollection
from datasets_ui import DsViewHandler


def main():
    """Run the application. """
    dc = DatasetCollection()
    ui = DsViewHandler().edit_traits( context = dc )
    GUI().start_event_loop()


if __name__ == '__main__':
    main()

#### EOF ######################################################################
