pydep
=====

pydep is a simple module / command line tool that will print the dependencies of a python project

WARNING: pydep may run a project's `setup.py`. Do not run on untrusted code.

Requirements
-----
- pip

Install
-----
```
pip install pydep
pip install git+git://github.com/sourcegraph/pydep  # install from dev master
```

Usage
-----

```
pydep-run.py -h  # print out options
pydep-run.py <src-directory>  # run pydep on directory
```
