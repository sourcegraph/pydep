"""
This setup.py executes in a `if __name__ == '__main__':` clause
(this is why we use `runpy.run_path` instead of `import` in setup_py.py)

"""

from setuptools import setup

if __name__ == '__main__':
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
