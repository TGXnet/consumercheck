
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
