# MKL libs for numpy

from PyInstaller import log as logging
from PyInstaller import compat
from os import listdir
from os.path import join

logger = logging.getLogger(__name__)
logger.info("MKL installed as part of numpy, importing that!")

mkldir = join(compat.base_prefix, "Library", "bin")
binaries = [(join(mkldir, mkl), '') for mkl in listdir(mkldir) if mkl.startswith('mkl_')]
