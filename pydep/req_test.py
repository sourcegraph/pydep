import unittest
import pkg_resources as pr
from os import path
from req import *

testdatadir = path.join(path.dirname(__file__), 'testdata')

class Test_requirements(unittest.TestCase):
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
            ('ex_nothing', '<<ERROR>>'),
        ]
        for testcase in testcases:
            dir_, exp = testcase[0], testcase[1]
            rootdir = path.join(testdatadir, dir_)
            reqs, err = requirements(rootdir, resolve=False)
            if err != None:
                self.assertEqual(exp, '<<ERROR>>')
            else:
                self.assertListEqual(sorted(exp), sorted(reqs))

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
            req_str = testcase[0]
            exp_dict = testcase[1]
            req = SetupToolsRequirement(pr.Requirement.parse(req_str))
            self.assertDictEqual(exp_dict, req.to_dict())

    def test_PipVCSInstallRequirement(self):
        pass
