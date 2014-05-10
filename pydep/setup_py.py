import sys
import pkg_resources as pr
import tempfile
import shutil
import subprocess
import os
import runpy
from os import path

def setup_info(setupfile):
    """Returns metadata for a PyPI package by running its setupfile"""
    setup_dict = {}
    def setup_replacement(**kw):
        for k, v in kw.iteritems():
            setup_dict[k] = v

    setuptools_mod = __import__('setuptools')
    import distutils.core # for some reason, __import__('distutils.core') doesn't work

    # Mod setup()
    old_setuptools_setup = setuptools_mod.setup
    setuptools_mod.setup = setup_replacement
    old_distutils_setup = distutils.core.setup
    distutils.core.setup = setup_replacement
    # Mod sys.path (changing sys.path is necessary in addition to changing the working dir, because of Python's import resolution order)
    old_sys_path = list(sys.path)
    sys.path.insert(0, path.dirname(setupfile))
    # Change working dir (necessary because some setup.py files read relative paths from the filesystem)
    old_wd = os.getcwd()
    os.chdir(path.dirname(setupfile))

    runpy.run_path(setupfile, run_name='__main__')

    # Restore working dir
    os.chdir(old_wd)
    # Restore sys.path
    sys.path = old_sys_path
    # Restore setup()
    distutils.core.setup = old_distutils_setup
    setuptools_mod.setup = old_setuptools_setup

    return setup_dict
