"""
A package representative of Python dependency management best practices.
"""

from setuptools import setup
import subprocess

print 'THIS SHOULD NOT APPEAR IN OUTPUT (but will in test)'
subprocess.call(['echo', 'THIS SHOULD NOT APPEAR IN OUTPUT EITHER (but will in test)'])

setup(
    name='ex0',
    version='0.1.2',
    url='http://github.com/fake/fake',
    packages=['ex0'],
    install_requires=[
        'dep1',
        'dep2==0.0',
        'dep3[blah]>=0.0.4',
    ],
)
