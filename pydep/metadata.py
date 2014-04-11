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
        resreqs.append(req_dict(req, req_info))
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

def req_dict(req, setup_info):
    repo_url = None
    if 'url' in setup_info:
        repo_url = parse_repo_url(setup_info['url'])
    if repo_url is None and 'download_url' in setup_info:
        repo_url = parse_repo_url(setup_info['download_url'])
    if repo_url is None and req.key in _hardcoded_repo_urls:
        repo_url = _hardcoded_repo_urls[req.key]
    py_modules = setup_info['py_modules'] if 'py_modules' in setup_info else None
    packages = setup_info['packages'] if 'packages' in setup_info else None
    return {
        'project_name': req.project_name,
        'unsafe_name': req.unsafe_name,
        'key': req.key,
        'specs': req.specs,
        'extras': req.extras,
        'repo_url': repo_url,
        'packages': packages,
        'modules': py_modules,
    }

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
