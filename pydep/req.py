"""
This module contains classes for dealing with pip and setuptools requirements classes
"""

import sys
import pkg_resources as pr
import tempfile
import shutil
import subprocess
from glob import glob
from os import path

import setup_py
from vcs import parse_repo_url

def requirements(rootdir, resolve=True):
    """
    Accepts the root directory of a PyPI package and returns its requirements.
    Returns (requirements, error_string) tuple. error_string is None if no error.
    """
    reqs, err = requirements_from_requirements_txt(rootdir)
    if err is not None:
        reqs, err = requirements_from_setup_py(rootdir)
    if err is not None:
        return None, 'could not get requirements due to error %s' % err

    if resolve:
        for req in reqs:
            err = req.resolve()
            if err != None:
                sys.stderr.write('error resolving requirement %s: %s\n' % (str(req), err))

    return [r.to_dict() for r in reqs], None

def requirements_from_setup_py(rootdir):
    """
    Accepts the root directory of a PyPI package and returns its requirements extracted from its setup.py
    Returns [], {'', None}
    """
    setupfile = path.join(rootdir, 'setup.py')
    if not path.exists(setupfile):
        return None, 'setup.py does not exist'

    setup_dict = setup_py.setup_info(setupfile)
    reqs = []
    if 'install_requires' in setup_dict:
        req_strs = setup_dict['install_requires']
        for req_str in req_strs:
            reqs.append(SetupToolsRequirement(pr.Requirement.parse(req_str)))
    return reqs, None

REQUIREMENTS_FILE_GLOB = '*requirements.txt'

def requirements_from_requirements_txt(rootdir):
    req_files = glob(path.join(rootdir, REQUIREMENTS_FILE_GLOB))
    if len(req_files) == 0:
        return None, 'no requirements file found'

    all_reqs = {}
    for f in req_files:
        with open(f) as req_file:
            req_text = req_file.read()
        try:
            reqs = pr.parse_requirements(req_text)
        except:
            return None, 'failed to parse requirements'
        for req in reqs:
            all_reqs[str(req)] = SetupToolsRequirement(req)
    return all_reqs.values(), None


class SetupToolsRequirement(object):
    """
    This represents a standard python requirement as defined by setuptools (e.g., "mypkg>=0.0.1").
    The constructor takes a pkg_resources.Requirement.
    """
    def __init__(self, req):
        self.req = req
        self.metadata = None

    def to_dict(self):
        repo_url, py_modules, packages = None, None, None
        if self.metadata is not None:
            if 'url' in self.metadata:
                repo_url = parse_repo_url(self.metadata['url'])
            if repo_url is None and 'download_url' in self.metadata:
                repo_url = parse_repo_url(self.metadata['download_url'])
            if repo_url is None and self.req.key in _hardcoded_repo_urls:
                repo_url = _hardcoded_repo_urls[self.req.key]
            py_modules = self.metadata['py_modules'] if 'py_modules' in self.metadata else None
            packages = self.metadata['packages'] if 'packages' in self.metadata else None

        return {
            'type': 'setuptools',
            'resolved': (self.metadata is not None),
            'project_name': self.req.project_name,
            'unsafe_name': self.req.unsafe_name,
            'key': self.req.key,
            'specs': self.req.specs,
            'extras': self.req.extras,
            'repo_url': repo_url,
            'packages': packages,
            'modules': py_modules,
        }

    def resolve(self):
        """Downloads this requirement from PyPI and returns metadata from its setup.py. Returns an error string or None if no error."""
        tmpdir = tempfile.mkdtemp()
        with open('/dev/null', 'w') as devnull:
            subprocess.call(['pip', 'install', '--build',  tmpdir, '--upgrade', '--force-reinstall', '--no-install', '--no-deps', str(self.req)],
                            stdout=devnull, stderr=devnull)
        setupfile = path.join(tmpdir, self.req.project_name, 'setup.py')
        if not path.exists(setupfile):
            return 'setup.py not found'
        setup_dict = setup_py.setup_info(setupfile)

        shutil.rmtree(tmpdir)
        self.metadata = setup_dict
        return None

class PipVCSInstallRequirement(object):
    """
    This represents a VCS requirement as seen by pip (e.g., 'git+git://github.com/foo/bar/').
    Such a requirement is not a valid requirement by setuptools standards. (In a setup.py, you would add the name/version
    of the requirement to install_requires as with PyPI packages, and then add the VCS link to dependency_links.)
    The constructor takes a pip.req.InstallRequirement.
    """
    def __init__(self, install_req):
        self.url = install_req.url
        self.metadata = None

    def to_dict(self):
        return {
            'type': 'vcs',
            'resolved': False,
            'project_name': None,
            'unsafe_name': None,
            'key': self.url,
            'specs': None,
            'extras': None,
            'repo_url': self.url,
            'packages': None,
            'modules': None,
        }

    def resolve(self):
        """
        Returns an error string or None if no error.
        TODO: resolve should download the requirement and extract the metadata from its setup.py, but right now,
        it does nothing, because the setup.py metadata of a package that is not on PyPI is of uncertain value and meaning.
        """
        return None

_hardcoded_repo_urls = {
    "ajenti":                "git://github.com/Eugeny/ajenti",
    "algorithm":             "git://github.com/gittip/algorithm.py",
    "ansible":               "git://github.com/ansible/ansible",
    "apache-libcloud":       "git://github.com/apache/libcloud",
    "aspen":                 "git://github.com/gittip/aspen-python",
    "autobahn":              "git://github.com/tavendo/AutobahnPython",
    "bottle":                "git://github.com/defnull/bottle",
    "celery":                "git://github.com/celery/celery",
    "chameleon":             "git://github.com/malthe/chameleon",
    "coverage":              "https://bitbucket.org/ned/coveragepy",
    "dependency_injection":  "git://github.com/gittip/dependency_injection.py",
    "distribute":            "https://bitbucket.org/tarek/distribute",
    "django":                "git://github.com/django/django",
    "django-cms":            "git://github.com/divio/django-cms",
    "django-tastypie":       "git://github.com/toastdriven/django-tastypie",
    "djangocms-admin-style": "git://github.com/divio/djangocms-admin-style",
    "djangorestframework":   "git://github.com/tomchristie/django-rest-framework",
    "dropbox":               "git://github.com/sourcegraph/dropbox",
    "eve":                   "git://github.com/nicolaiarocci/eve",
    "fabric":                "git://github.com/fabric/fabric",
    "filesystem_tree":       "git://github.com/gittip/filesystem_tree.py",
    "flask":                 "git://github.com/mitsuhiko/flask",
    "gevent":                "git://github.com/surfly/gevent",
    "gunicorn":              "git://github.com/benoitc/gunicorn",
    "httpie":                "git://github.com/jkbr/httpie",
    "httplib2":              "git://github.com/jcgregorio/httplib2",
    "itsdangerous":          "git://github.com/mitsuhiko/itsdangerous",
    "jinja2":                "git://github.com/mitsuhiko/jinja2",
    "kazoo":                 "git://github.com/python-zk/kazoo",
    "kombu":                 "git://github.com/celery/kombu",
    "lamson":                "git://github.com/zedshaw/lamson",
    "libcloud":              "git://github.com/apache/libcloud",
    "lxml":                  "git://github.com/lxml/lxml",
    "mako":                  "git://github.com/zzzeek/mako",
    "markupsafe":            "git://github.com/mitsuhiko/markupsafe",
    "matplotlib":            "git://github.com/matplotlib/matplotlib",
    "mimeparse":             "git://github.com/crosbymichael/mimeparse",
    "mock":                  "https://code.google.com/p/mock",
    "nltk":                  "git://github.com/nltk/nltk",
    "nose":                  "git://github.com/nose-devs/nose",
    "nova":                  "git://github.com/openstack/nova",
    "numpy":                 "git://github.com/numpy/numpy",
    "pandas":                "git://github.com/pydata/pandas",
    "pastedeploy":           "https://bitbucket.org/ianb/pastedeploy",
    "pattern":               "git://github.com/clips/pattern",
    "postgres":              "git://github.com:gittip/postgres.py",
    "psycopg2":              "git://github.com/psycopg/psycopg2",
    "pyramid":               "git://github.com/Pylons/pyramid",
    "python-catcher":        "git://github.com/Eugeny/catcher",
    "python-dateutil":       "git://github.com/paxan/python-dateutil",
    "python-lust":           "git://github.com/zedshaw/python-lust",
    "pyyaml":                "git://github.com/yaml/pyyaml",
    "reconfigure":           "git://github.com/Eugeny/reconfigure",
    "repoze.lru":            "git://github.com/repoze/repoze.lru",
    "requests":              "git://github.com/kennethreitz/requests",
    "salt":                  "git://github.com/saltstack/salt",
    "scikit-learn":          "git://github.com/scikit-learn/scikit-learn",
    "scipy":                 "git://github.com/scipy/scipy",
    "sentry":                "git://github.com/getsentry/sentry",
    "setuptools":            "git://github.com/jaraco/setuptools",
    "sockjs-tornado":        "git://github.com/mrjoes/sockjs-tornado",
    "south":                 "https://bitbucket.org/andrewgodwin/south",
    "sqlalchemy":            "git://github.com/zzzeek/sqlalchemy",
    "ssh":                   "git://github.com/bitprophet/ssh",
    "tornado":               "git://github.com/facebook/tornado",
    "translationstring":     "git://github.com/Pylons/translationstring",
    "tulip":                 "git://github.com/sourcegraph/tulip",
    "twisted":               "git://github.com/twisted/twisted",
    "venusian":              "git://github.com/Pylons/venusian",
    "webob":                 "git://github.com/Pylons/webob",
    "webpy":                 "git://github.com/webpy/webpy",
    "werkzeug":              "git://github.com/mitsuhiko/werkzeug",
    "zope.interface":        "git://github.com/zopefoundation/zope.interface",
}
