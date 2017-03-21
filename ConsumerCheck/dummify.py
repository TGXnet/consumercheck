
from __future__ import absolute_import, division, print_function


import pandas as pd

import dataset as ds



def dummify(dataset, attributes):
    """Return dataset where selected attributes is dummified

    :param dataset: the dataset to dummify
    :param attributes: list of attributes to dummify
    :returns: dataset with dummify selected variables
    :raises keyError: raises an exception
    """
    return dataset


if __name__ == '__main__':
    print("Start")
    tor = ds.DataSet(display_name='Some values', kind='Consumer characteristics')
    tor.mat = pd.DataFrame(
        [[1, 'M', 'Good'],
         [2, 'F', 'Poor'],
         [1, 'M', 'Alive'],
         [2, 'F', 'Good']],
        index = ['V1', 'V2', 'V3', 'V4'],
        columns = ['AgeGr', 'Sex', 'Health'])

    res = dummify(tor, [])
    print(res.mat)
