import re

repo_url_patterns = [
    r'(https?\://github.com/(?:[^/]+)/(?:[^/]+))(?:/.*)?',
    r'(https?\://bitbucket.org/(?:[^/]+)/(?:[^/]+))(?:/.*)?',
    r'(https?\://code.google.com/p/(?:[^/]+))(?:/.*)?',
]

def parse_repo_url(url):
    for pattern in repo_url_patterns:
        match = re.match(pattern, url)
        if match is not None:
            return match.group(1)
    return None
