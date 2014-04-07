import sys
import pkg_resources as pr
import tempfile
import shutil
import subprocess
from os import path

def requirements(rootdir):
    setupfile = path.join(rootdir, 'setup.py')
    if not path.exists(setupfile):
        return None, 'setup.py does not exist'

    setup_dict = setup_info(setupfile)
    reqs = []
    if 'install_requires' in setup_dict:
        req_strs = setup_dict['install_requires']
        for req_str in req_strs:
            req = pr.Requirement.parse(req_str)
            reqs.append(req)
    return reqs, None

_first_time = True

def setup_info(setupfile):
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
    # Mod sys.path
    old_sys_path = list(sys.path)
    sys.path.insert(0, path.dirname(setupfile))

    global _first_time
    import setup as this_setup
    if _first_time:
        _first_time = False
    else:
        reload(this_setup)

    # Restore sys.path
    sys.path = old_sys_path
    # Restore setup()
    distutils.core.setup = old_distutils_setup
    setuptools_mod.setup = old_setuptools_setup

    return setup_dict

def setup_info_from_requirement(requirement):
    tmpdir = tempfile.mkdtemp()
    with open('/dev/null', 'w') as devnull:
        subprocess.call(['pip', 'install', '--build',  tmpdir, '--upgrade', '--force-reinstall', '--no-install', '--no-deps', str(requirement)],
                        stdout=devnull, stderr=devnull)
    setupfile = path.join(tmpdir, requirement.project_name, 'setup.py')
    if not path.exists(setupfile):
        return None, 'setup.py not found'
    setup_dict = setup_info(setupfile)

    shutil.rmtree(tmpdir)
    return setup_dict, None
