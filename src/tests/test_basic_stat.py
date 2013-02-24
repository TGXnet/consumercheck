
import pytest

from basic_stat_model import BasicStat, extract_summary, extract_histogram


def test_discrete(discrete_ds):

    bs = BasicStat(ds=discrete_ds)
    print("\n")
    res = bs.stat_res
    summary = extract_summary(res)
    print(summary._matrix)
    hist = extract_histogram(res)
    print(hist._matrix)


def test_continous():
    pass


def test_missing():
    pass
