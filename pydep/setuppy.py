import sys
import pkg_resources as pr
from os import path
from requirements import requirements_dict

def list_deps(dir):
    setupfile = path.join(dir, 'setup.py')
    if not path.exists(setupfile):
        return None, 'setup.py does not exist'

    req_dicts = []
    def setup_replacement(**kw):
        if 'install_requires' in kw:
            req_strs = kw['install_requires']
            for req_str in req_strs:
                req = pr.Requirement.parse(req_str)
                req_dict = requirements_dict(req)
                req_dicts.append(req_dict)

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

    __import__('setup')

    # Restore sys.path
    sys.path = old_sys_path
    # Restore setup()
    distutils.core.setup = old_distutils_setup
    setuptools_mod.setup = old_setuptools_setup

    return req_dicts, None
