import pkg_resources as pr
from os import path
from glob import glob

REQUIREMENTS_FILE_GLOB = '*requirements.txt'

def list_deps(dir): # returns [], {'', None}
    req_files = glob(path.join(dir, REQUIREMENTS_FILE_GLOB))
    if len(req_files) == 0:
        return None, 'no requirements file found'

    req_dicts = {}
    for f in req_files:
        with open(f) as req_file:
            req_text = req_file.read()
        try:
            reqs = pr.parse_requirements(req_text)
        except:
            return None, 'failed to parse requirements'
        for req in reqs:
            req_dicts[str(req)] = requirements_dict(req)
    return req_dicts.values(), None

def requirements_dict(req):
    return {
        'project_name': req.project_name,
        'unsafe_name': req.unsafe_name,
        'key': req.key,
        'specs': req.specs,
        'extras': req.extras,
    }
