import unittest
from pydep.vcs import parse_repo_url


class TestVCS(unittest.TestCase):
    def test_parse_repo_url(self):
        testcases = [
            ('http://github.com/foo/bar', 'http://github.com/foo/bar'),
            ('https://github.com/foo/bar/baz', 'https://github.com/foo/bar'),
            ('git+https://github.com/foo/bar/baz', 'https://github.com/foo/bar'),
            ('git+git://github.com/foo/bar.git#egg=foo', 'git://github.com/foo/bar.git'),

            ('https://code.google.com/p/bar', 'https://code.google.com/p/bar'),
            ('https://code.google.com/p/bar/blah/blah', 'https://code.google.com/p/bar'),
            ('git+https://code.google.com/p/bar/blah/blah', 'https://code.google.com/p/bar'),
            ('git+git://code.google.com/p/bar.git#egg=foo', 'git://code.google.com/p/bar.git'),

            ('https://bitbucket.org/foo/bar', 'https://bitbucket.org/foo/bar'),
            ('https://bitbucket.org/foo/bar/baz', 'https://bitbucket.org/foo/bar'),
            ('hg+https://bitbucket.org/foo/bar', 'https://bitbucket.org/foo/bar'),
            ('git+git://bitbucket.org/foo/bar', 'git://bitbucket.org/foo/bar'),

            ('https://google.com', None),
        ]

        for testcase in testcases:
            self.assertEqual(testcase[1], parse_repo_url(testcase[0]))
