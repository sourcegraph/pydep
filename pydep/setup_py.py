import sys
import pkg_resources as pr
import tempfile
import shutil
import subprocess
import os
import runpy
from os import path

def setup_dirs(container_dir):
    """
    Given a directory that may contain Python packages (defined by setup.py
    files), returns a list of package root directories (i.e., directories that
    contain a setup.py)
    """
    rootdirs = []
    for dirpath, _, filenames in os.walk(container_dir):
        for filename in filenames:
            if filename == 'setup.py':
                rootdirs.append(dirpath)
                break
    return rootdirs

def setup_info_dir(rootdir):
    """
    Returns (metadata, error_string) tuple. error_string is None if no error.
    """
    setupfile = path.join(rootdir, 'setup.py')
    if not path.exists(setupfile):
        return None, 'setup.py does not exist'
    return setup_info(setupfile), None

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
    # Redirect stdout to stderr (*including for subprocesses*)
    old_sys_stdout = sys.stdout # redirects in python process
    sys.stdout = sys.stderr
    old_stdout = os.dup(1)      # redirects in subprocesses
    stderr_dup = os.dup(2)
    os.dup2(stderr_dup, 1)

    runpy.run_path(path.basename(setupfile), run_name='__main__')

    # Restore stdout
    os.dup2(old_stdout, 1)      # restores for subprocesses
    os.close(stderr_dup)
    sys.stdout = old_sys_stdout # restores for python process
    # Restore working dir
    os.chdir(old_wd)
    # Restore sys.path
    sys.path = old_sys_path
    # Restore setup()
    distutils.core.setup = old_distutils_setup
    setuptools_mod.setup = old_setuptools_setup

    return setup_dict
