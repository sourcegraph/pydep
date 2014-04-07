import pkg_resources as pr
from os import path
from glob import glob

REQUIREMENTS_FILE_GLOB = '*requirements.txt'

def requirements(rootdir): # returns [], {'', None}
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
            all_reqs[str(req)] = req
    return all_reqs.values(), None
