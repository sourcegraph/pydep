import re

repo_url_patterns = [
    r'(?:git\+)?((?:https?|git)\://github.com/(?:[^/#]+)/(?:[^/#]+))(?:/.*)?',
    r'(?:git\+|hg\+)?((?:https?|git|hg)\://bitbucket.org/(?:[^/#]+)/(?:[^/#]+))(?:/.*)?',
    r'(?:git\+|hg\+)?((?:https?|git|hg)\://code.google.com/p/(?:[^/#]+))(?:/.*)?',
]


def parse_repo_url(url):
    """Returns the canonical repository clone URL from a string that contains it"""
    for pattern in repo_url_patterns:
        match = re.match(pattern, url)
        if match is not None:
            return match.group(1)
    return None
