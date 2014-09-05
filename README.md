pydep
=====

`pydep` is a simple module / command line tool that will print the dependencies of a python project.<br>
`pydep` is still under active development. There are bugs. Pull requests welcome :)

__WARNING: Do not run pydep on untrusted code, as it may execute a project's setup.py.__

Install
-----
```
pip install pydep                                   # install latest release
pip install git+git://github.com/sourcegraph/pydep  # install from dev master
```

Usage
-----

```
pydep-run.py -h  # print out options
pydep-run.py dep <src-directory>  # run pydep on directory
pydep-run.py demo                 # print some info out that demonstrates capabilities
```

For example,
```
> pip install pydep
> git clone https://github.com/mitsuhiko/flask
> cd flask
> pydep-run.py dep .
[{"resolved": true, "project_name": "Werkzeug", "unsafe_name": "Werkzeug", "key": "werkzeug", "modules": null, "packages": ["werkzeug", "werkzeug.debug", "werkzeug.contrib", "werkzeug.testsuite", "werkzeug.testsuite.contrib"],
"type": "setuptools", "specs": [[">=", "0.7"]], "repo_url": "git://github.com/mitsuhiko/werkzeug", "extras": []},
{"resolved": true, "project_name": "Jinja2", "unsafe_name": "Jinja2", "key": "jinja2", "modules": null, "packages":
["jinja2", "jinja2.testsuite", "jinja2.testsuite.res"], "type": "setuptools", "specs": [[">=", "2.4"]], "repo_url":
"git://github.com/mitsuhiko/jinja2", "extras": []}, {"resolved": true, "project_name": "itsdangerous", "unsafe_name":
"itsdangerous", "key": "itsdangerous", "modules": ["itsdangerous"], "packages": null, "type": "setuptools", "specs":
[[">=", "0.21"]], "repo_url": "http://github.com/mitsuhiko/itsdangerous", "extras": []}, {"resolved": true,
"project_name": "click", "unsafe_name": "click", "key": "click", "modules": null, "packages": ["click"], "type":
"setuptools", "specs": [[">=", "0.6"]], "repo_url": "http://github.com/mitsuhiko/click", "extras": []}]
```

Additional requirements
-----
- Unix (Windows is untested and will probably fail, because, e.g., things get piped to /dev/null in a few places)
- pip 1.5+

Tests
-----
Install nose (`pip install nose`). Then, `nosetests -s` from the root repository directory.

Contributing
------------
Make a pull request!
