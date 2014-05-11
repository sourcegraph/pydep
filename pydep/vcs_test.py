import unittest
from vcs import parse_repo_url

class TestVCS(unittest.TestCase):
    def test_parse_repo_url(self):
        testcases = [
            ('http://github.com/foo/bar', 'http://github.com/foo/bar'),
            ('https://github.com/foo/bar/baz', 'https://github.com/foo/bar'),
            ('https://code.google.com/p/bar', 'https://code.google.com/p/bar'),
            ('https://code.google.com/p/bar/blah/blah', 'https://code.google.com/p/bar'),
            ('https://bitbucket.org/foo/bar', 'https://bitbucket.org/foo/bar'),
            ('https://bitbucket.org/foo/bar/baz', 'https://bitbucket.org/foo/bar'),
            ('https://google.com', None),
        ]

        for testcase in testcases:
            self.assertEqual(testcase[1], parse_repo_url(testcase[0]))
