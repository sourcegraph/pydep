import re

repo_url_patterns = [
    r'(?:git\+)?(https?\://github.com/(?:[^/]+)/(?:[^/]+))(?:/.*)?',
    r'(?:git\+|hg\+)?(https?\://bitbucket.org/(?:[^/]+)/(?:[^/]+))(?:/.*)?',
    r'(?:git\+|hg\+)?(https?\://code.google.com/p/(?:[^/]+))(?:/.*)?',
]

def parse_repo_url(url):
    """Returns the canonical repository clone URL from a string that contains it"""
    for pattern in repo_url_patterns:
        match = re.match(pattern, url)
        if match is not None:
            return match.group(1)
    return None
