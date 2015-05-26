import unittest
from pip import req as req

from pydep.req import *

testdatadir = path.join(path.dirname(__file__), 'testdata')


class TestRequirements(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_requirements(self):
        """
        Tests the requirements() function (the main external function of this package).
        The purpose of this test is to test that the correct dependency extraction method is applied, NOT to
        test the correctness of the individual dependency extraction methods.
        """
        expected0 = [
            {'extras': (),
             'key': 'dep2',
             'modules': None,
             'packages': None,
             'project_name': 'dep2',
             'repo_url': None,
             'resolved': False,
             'specs': [('==', '0.0')],
             'type': 'setuptools',
             'unsafe_name': 'dep2'},
            {'extras': (),
             'key': 'dep1',
             'modules': None,
             'packages': None,
             'project_name': 'dep1',
             'repo_url': None,
             'resolved': False,
             'specs': [],
             'type': 'setuptools',
             'unsafe_name': 'dep1'},
            {'extras': ('blah',),
             'key': 'dep3',
             'modules': None,
             'packages': None,
             'project_name': 'dep3',
             'repo_url': None,
             'resolved': False,
             'specs': [('>=', '0.0.4')],
             'type': 'setuptools',
             'unsafe_name': 'dep3'}
        ]
        testcases = [
            ('ex0', expected0),
            ('ex_nosetuppy', expected0),
            ('ex_norequirementstxt', expected0),
            ('ex_weirdsetuppy', expected0),
            ('ex_setuppy_prints', expected0),
            ('ex_nothing', '<<ERROR>>'),
            ('ex_requirementstxtvcs', [
                {'key': 'https://code.google.com/p/foo',
                 'repo_url': 'https://code.google.com/p/foo',
                 'type': 'vcs',
                 'modules': None, 'extras': None, 'packages': None, 'project_name': None, 'resolved': False,
                 'specs': None, 'unsafe_name': None},
                {'key': 'https://github.com/foo/bar',
                 'repo_url': 'https://github.com/foo/bar',
                 'type': 'vcs', 'extras': None, 'modules': None, 'packages': None, 'project_name': None,
                 'resolved': False, 'specs': None, 'unsafe_name': None},
                {'extras': (),
                 'key': 'foo',
                 'project_name': 'foo',
                 'type': 'setuptools',
                 'unsafe_name': 'foo',
                 'modules': None,
                 'packages': None,
                 'repo_url': None,
                 'resolved': False,
                 'specs': []}
            ]),
        ]
        for testcase in testcases:
            dir_, exp = testcase[0], testcase[1]
            rootdir = path.join(testdatadir, dir_)
            reqs, err = requirements(rootdir, resolve=False)
            if err is not None:
                if exp != '<<ERROR>>':
                    print('unexpected error: ', err)
                self.assertEqual(exp, '<<ERROR>>')
            else:
                self.assertListEqual(sorted(exp, key=lambda x: x['key']), sorted(reqs, key=lambda x: x['key']))

    def test_SetupToolsRequirement(self):
        testcases = [
            ("foo==0.0.0", {
                'extras': (),
                'key': 'foo',
                'modules': None,
                'packages': None,
                'project_name': 'foo',
                'repo_url': None,
                'resolved': False,
                'specs': [('==', '0.0.0')],
                'type': 'setuptools',
                'unsafe_name': 'foo'
            }),
            ("foo[bar]>=0.1b", {
                'extras': ('bar',),
                'key': 'foo',
                'modules': None,
                'packages': None,
                'project_name': 'foo',
                'repo_url': None,
                'resolved': False,
                'specs': [('>=', '0.1b')],
                'type': 'setuptools',
                'unsafe_name': 'foo'
            }),
        ]
        for testcase in testcases:
            req_str, exp_dict = testcase[0], testcase[1]
            st_req = SetupToolsRequirement(pr.Requirement.parse(req_str))
            self.assertDictEqual(exp_dict, st_req.to_dict())

    def test_PipVCSInstallRequirement(self):
        requirements_str = """
        git+https://github.com/foo/bar
        git+https://code.google.com/p/foo
        git+git://code.google.com/p/foo#egg=bar
        """
        expected = [
            {
                'type': 'vcs',
                'key': 'https://github.com/foo/bar',
                'repo_url': 'https://github.com/foo/bar',
                'unsafe_name': None, 'extras': None, 'modules': None, 'packages': None, 'project_name': None,
                'resolved': False, 'specs': None,
            },
            {
                'type': 'vcs',
                'key': 'https://code.google.com/p/foo',
                'repo_url': 'https://code.google.com/p/foo',
                'unsafe_name': None, 'extras': None, 'modules': None, 'packages': None, 'project_name': None,
                'resolved': False, 'specs': None,
            },
            {
                'type': 'vcs',
                'key': 'bar(git://code.google.com/p/foo)',
                'repo_url': 'git://code.google.com/p/foo',
                'unsafe_name': 'bar',
                'project_name': 'bar',
                'specs': [], 'extras': (), 'modules': None, 'packages': None, 'resolved': False,
            },
        ]

        _, requirements_file = tempfile.mkstemp()
        with open(requirements_file, 'w') as f:
            f.write(requirements_str)
        pip_reqs = req.parse_requirements(requirements_file, session=pip.download.PipSession())
        reqs = [PipURLInstallRequirement(r).to_dict() for r in pip_reqs]
        os.remove(requirements_file)

        self.assertListEqual(expected, reqs)
