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

def parse_repo_url_and_revision(url):
    """Returns the canonical repository clone URL and revision from a string that contains it"""
    full_url = parse_repo_url(url)
    components = full_url.split('@')
    if len(components) == 2:
        return components[0], components[1]
    elif len(components) == 1:
        return components[0], ''
    return full_url, '' # fall back to returning the full URL
