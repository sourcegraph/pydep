import setup_py
import requirements_txt
import re
import sys

def raw_requirements(rootdir):
    rawreqs, err = _raw_reqs(rootdir)
    if err is not None:
        return None, err
    return [req_dict(req, None) for req in rawreqs], None

def resolved_requirements(rootdir):
    rawreqs, err = _raw_reqs(rootdir)
    if err is not None:
        return None, err

    resreqs = []
    for req in rawreqs:
        req_info, err = setup_py.setup_info_from_requirement(req)
        if err is not None:
            sys.stderr.write('error resolving requirement %s: %s\n' % (str(req), err))
            continue

        repo_url = None
        if 'url' in req_info:
            repo_url = parse_repo_url(req_info['url'])
        if repo_url is None and 'download_url' in req_info:
            repo_url = parse_repo_url(req_info['download_url'])
        resreqs.append(req_dict(req, repo_url))
    return resreqs, None

repo_url_patterns = [
    r'(https?\://github.com/(?:[^/]+)/(?:[^/]+))(?:/.*)?',
    r'(https?\://bitbucket.org/(?:[^/]+)/(?:[^/]+))(?:/.*)?',
    r'(https?\://code.google.com/p/(?:[^/]+))(?:/.*)?',
]

def _raw_reqs(rootdir):
    reqs, err = requirements_txt.requirements(rootdir)
    if err is not None:
        reqs, err = setup_py.requirements(rootdir)
    if err is not None:
        return None, 'could not get requirements due to error %s' % err
    return reqs, None

def parse_repo_url(url):
    for pattern in repo_url_patterns:
        match = re.match(pattern, url)
        if match is not None:
            return match.group(1)
    return None

def req_dict(req, repo_url):
    return {
        'project_name': req.project_name,
        'unsafe_name': req.unsafe_name,
        'key': req.key,
        'specs': req.specs,
        'extras': req.extras,
        'repo_url': repo_url,
    }
