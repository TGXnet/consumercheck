
import pytest
import os

import cc_config as conf

# setup: read original value and stor it
# do tests by setting new value
# restore original value when test i completed


def test_read_dir():
    wd = conf.get_option('work_dir')
    print(wd)
    assert(isinstance(wd, str))


def test_update_option():
    hold = conf.get_option('work_dir')
    conf.set_option('work_dir', os.getcwd())
    check = conf.get_option('work_dir')
    print(hold, check)
    conf.set_option('work_dir', hold)
    assert(check == os.getcwd())


def test_missing():
    wanted = conf.get_option('plot_height')
    print(wanted)
