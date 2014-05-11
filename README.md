pydep
=====

`pydep` is a simple module / command line tool that will print the dependencies of a python project.<br>
`pydep` is still under active development. There are bugs. Pull requests welcome :)

__WARNING: `pydep` may execute a project's `setup.py`. Do not run on untrusted code.__

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
pydep-run.py <src-directory>  # run pydep on directory
```

For example,
```
> pip install pydep
> git clone https://github.com/mitsuhiko/flask
> cd flask
> pydep-run.py .
[{"project_name": "Werkzeug", "unsafe_name": "Werkzeug", "key": "werkzeug", "modules": null, "packages": ["werkzeug", "werkzeug.debug", "werkzeug.contrib", "werkzeug.testsuite", "werkzeug.testsuite.contrib"],
"repo_url": "git://github.com/mitsuhiko/werkzeug", "specs": [[">=", "0.7"]], "extras": []}, {"project_name": "Jinja2", "unsafe_name": "Jinja2", "key":
"jinja2", "modules": null, "packages": ["jinja2", "jinja2.testsuite", "jinja2.testsuite.res"], "repo_url": "git://github.com/mitsuhiko/jinja2",
"specs": [[">=", "2.4"]], "extras": []}, {"project_name": "itsdangerous", "unsafe_name": "itsdangerous", "key": "itsdangerous", "modules":
["itsdangerous"], "packages": null, "repo_url": "http://github.com/mitsuhiko/itsdangerous", "specs": [[">=", "0.21"]], "extras": []}]
```

Additional requirements
-----
- pip

Tests
-----
Install nose (`pip install nose`). Then, `nosetests -s` from the root repository directory.

Contributing
------------
Make a pull request!
