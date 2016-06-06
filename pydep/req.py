"""
This module contains classes for dealing with pip and setuptools requirements classes
"""

import sys
import pkg_resources as pr
import pip
import tempfile
import shutil
import subprocess
import os
import re
from glob import glob
from os import path

from pydep import setup_py
from pydep.util import rmtree
from pydep.vcs import parse_repo_url


def requirements(rootdir, resolve=True):
    """Accepts the root directory of a PyPI package and returns its requirements. If
    both *requirements.txt and setup.py exist, it combines the dependencies
    defined in both, giving precedence to those defined in requirements.txt.
    Returns (requirements, error_string) tuple. error_string is None if no
    error.

    """
    reqs = {}
    reqstxt_reqs, reqstxt_err = requirements_from_requirements_txt(rootdir)
    if reqstxt_err is None:
        for r in reqstxt_reqs:
            reqs[r.req.project_name] = r
    setuppy_reqs, setuppy_err = requirements_from_setup_py(rootdir)
    if setuppy_err is None:
        for r in setuppy_reqs:
            if r.req.project_name not in reqs:
                reqs[r.req.project_name] = r
    if reqstxt_err is not None and setuppy_err is not None:
        return None, 'could not get requirements due to 2 errors: %s, %s' % (reqstxt_err, setuppy_err)

    reqs = list(reqs.values())

    if resolve:
        for req in reqs:
            err = req.resolve()
            if err is not None:
                sys.stderr.write('error resolving requirement %s: %s\n' % (str(req), err))

    return [r.to_dict() for r in reqs], None


def requirements_from_setup_py(rootdir):
    """
    Accepts the root directory of a PyPI package and returns its requirements extracted from its setup.py
    Returns [], {'', None}
    """
    setup_dict, err = setup_py.setup_info_dir(rootdir)
    if err is not None:
        return None, err

    reqs = []
    if 'install_requires' in setup_dict:
        req_strs = setup_dict['install_requires']
        for req_str in req_strs:
            reqs.append(SetupToolsRequirement(pr.Requirement.parse(req_str)))
    return reqs, None


REQUIREMENTS_FILE_GLOB = '*requirements*.txt'


def requirements_from_requirements_txt(rootdir):
    req_files = glob(path.join(rootdir, REQUIREMENTS_FILE_GLOB))
    if len(req_files) == 0:
        return None, 'no requirements file found'

    all_reqs = {}
    for f in req_files:
        for install_req in pip.req.parse_requirements(f, session=pip.download.PipSession()):
            if install_req.link is not None:
                req = PipURLInstallRequirement(install_req)
            else:
                req = SetupToolsRequirement(install_req.req)
            all_reqs[str(req)] = req

    return all_reqs.values(), None


class SetupToolsRequirement(object):
    """
    This represents a standard python requirement as defined by setuptools (e.g., "mypkg>=0.0.1").
    The constructor takes a pkg_resources.Requirement.
    """
    def __init__(self, req):
        self.req = req
        self.metadata = None

    def __str__(self):
        return self.req.__str__()

    def to_dict(self):
        repo_url, py_modules, packages = None, None, None
        if self.metadata is not None:
            if 'url' in self.metadata:
                repo_url = parse_repo_url(self.metadata['url'])
            if repo_url is None and 'download_url' in self.metadata:
                repo_url = parse_repo_url(self.metadata['download_url'])
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
        """
        Downloads this requirement from PyPI and returns metadata from its setup.py.
        Returns an error string or None if no error.
        """
        tmp_dir = tempfile.mkdtemp()
        with open(os.devnull, 'w') as devnull:
            try:
                cmd = ['install', '--quiet',
                       '--download',  tmp_dir,
                       '--build',  tmp_dir,
                       '--no-clean', '--no-deps',
                       '--no-binary', ':all:', str(self.req)]
                pip.main(cmd)
            except Exception as e:
                rmtree(tmp_dir)
                return 'error downloading requirement: {}'.format(str(e))

        project_dir = path.join(tmp_dir, self.req.project_name)
        setup_dict, err = setup_py.setup_info_dir(project_dir)
        if err is not None:
            return None, err
        rmtree(tmp_dir)

        self.metadata = setup_dict
        return None


class PipURLInstallRequirement(object):
    """
    This represents a URL requirement as seen by pip (e.g., 'git+git://github.com/foo/bar/').
    Such a requirement is not a valid requirement by setuptools standards. (In a setup.py,
    you would add the name/version of the requirement to install_requires as with PyPI packages,
    and then add the URL link to dependency_links.
    Also included archive files such as *.zip, *.tar, *.zip.gz, or *.tar.gz)
    The constructor takes a pip.req.InstallRequirement.
    """
    _archive_regex = re.compile('^(http|https)://[^/]+/.+\.(zip|tar)(\.gz|)$', re.IGNORECASE)

    def __init__(self, install_req):
        self._install_req = install_req
        if install_req.link is None:
            raise 'No URL found in install_req: %s' % str(install_req)
        self.url = parse_repo_url(install_req.link.url)
        self.metadata = None
        self.vcs = None
        self.type = 'vcs'
        if install_req.link.url.find('+') >= 0:
            self.vcs = install_req.link.url[:install_req.link.url.find('+')]
        elif self._archive_regex.match(install_req.link.url) is not None:
            self.type = 'archive'
        self.setuptools_req = install_req.req  # may be None

    def __str__(self):
        return self.url.__str__()

    def to_dict(self):
        project_name, unsafe_name, specs, extras, key = None, None, None, None, self.url
        if self.setuptools_req is not None:
            r = self.setuptools_req
            project_name, unsafe_name, specs, extras = r.project_name, r.unsafe_name, r.specs, r.extras
            key = '%s(%s)' % (r.key, self.url)

        py_modules, packages = None, None
        if self.metadata is not None:
            py_modules = self.metadata['py_modules'] if 'py_modules' in self.metadata else None
            packages = self.metadata['packages'] if 'packages' in self.metadata else None
            if project_name is None and 'name' in self.metadata:
                project_name = self.metadata['name']

        return {
            'type': self.type,
            'resolved': (self.metadata is not None),
            'project_name': project_name,
            'unsafe_name': unsafe_name,
            'key': key,
            'specs': specs,
            'extras': extras,
            'repo_url': self.url,
            'packages': packages,
            'modules': py_modules,
        }

    def resolve(self):
        """
        Downloads this requirement from the VCS repository or archive file and returns metadata from its setup.py.
        Returns an error string or None if no error.
        """
        tmpdir = tempfile.mkdtemp()
        with open(os.devnull, 'w') as devnull:
            # Because of a bug in pip when dealing with VCS URLs, we can't use pip to download the repository
            if self.vcs == 'git':
                subprocess.call(['git', 'clone', '--depth=1', str(self.url), tmpdir], stdout=devnull, stderr=devnull)
            elif self.vcs == 'hg':
                subprocess.call(['hg', 'clone', str(self.url), tmpdir], stdout=devnull, stderr=devnull)
            elif self.vcs is None and self.type == 'archive':
                install_url = self._install_req.url
                tmparchive = tempfile.mkstemp()[1]
                subprocess.call(['curl', '-L', install_url, '-o', tmparchive], stdout=devnull, stderr=devnull)
                if install_url.endswith(".gz"):
                    subprocess.call(['gunzip', '-c', tmparchive], stdout=devnull, stderr=devnull)
                    install_url = install_url[0:-3]
                if install_url.endswith(".tar"):
                    subprocess.call(['tar', '-xvf', tmparchive, '-C', tmpdir], stdout=devnull, stderr=devnull)
                elif install_url.endswith(".zip"):
                    subprocess.call(['unzip', '-j', '-o', tmparchive, '-d', tmpdir], stdout=devnull, stderr=devnull)
            else:
                return 'cannot resolve requirement {} (from {}) with unrecognized VCS: {}'.format(
                    str(self),
                    str(self._install_req),
                    self.vcs
                )
        setup_dict, err = setup_py.setup_info_dir(tmpdir)
        if err is not None:
            return None, err
        rmtree(tmpdir)
        self.metadata = setup_dict
        return None
