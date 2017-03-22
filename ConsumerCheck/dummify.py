
from __future__ import absolute_import, division, print_function


def dummify(dataset, attributes):
    """Return dataset where selected attributes is dummified

    :param dataset: the dataset to dummify
    :param attributes: list of attributes to dummify
    :returns: dataset with dummify selected variables
    :raises keyError: attribute not found in given dataset
    """
    mat = dataset.mat
    for attr in attributes:
        pos = list(dataset.mat.columns).index(attr)
        for val in set(mat[attr]):
            attn = str("{}_{}".format(attr, val))
            dummies = [int(i) for i in list(mat[attr] == val)]
            pos += 1
            mat.insert(pos, attn, dummies)
        del(mat[attr])
    return dataset


if __name__ == '__main__':
    print("Start")
    import pandas as pd
    import dataset as ds

    tor = ds.DataSet(display_name='Some values', kind='Consumer characteristics')
    tor.mat = pd.DataFrame(
        [[1, 'M', 'Good'],
         [2, 'F', 'Poor'],
         [1, 'M', 'Alive'],
         [2, 'F', 'Good']],
        index = ['V1', 'V2', 'V3', 'V4'],
        columns = ['AgeGr', 'Sex', 'Health'])

    print(tor.mat)
    res = dummify(tor, ['AgeGr', 'Sex', 'Health'])
    print(res.mat)
