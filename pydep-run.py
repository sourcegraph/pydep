#!/usr/bin/env python

import sys
import json
import argparse
import pydep.req
import pydep.setup_py

from os import path
import subprocess
import tempfile
import shutil


def main():
    # Parse args
    argparser = argparse.ArgumentParser(
        description='pydep is simple command line tool that tells you about package dependency metadata in Python')
    subparsers = argparser.add_subparsers()

    dep_parser = subparsers.add_parser('dep', help='print the dependencies of a python project in JSON')
    dep_parser.add_argument('--raw', action='store_true',
                            help='If true, pydep will not try to resolve dependencies to VCS URLs')
    dep_parser.add_argument('dir', help='path to root directory of project code')
    dep_parser.set_defaults(func=dep)

    info_parser = subparsers.add_parser('info', help='print metadata of a python project in JSON')
    info_parser.add_argument('dir', help='path to root directory of project code')
    info_parser.set_defaults(func=info)

    list_info_parser = subparsers.add_parser('list', help='print metadata of all python projects in a directory')
    list_info_parser.add_argument('dir', help='path to containing directory')
    list_info_parser.set_defaults(func=list_info)

    smoke_parser = subparsers.add_parser('demo',
                                         help='run pydep against some popular repositories, printing out dependency'
                                              ' information about each')
    smoke_parser.set_defaults(func=smoke_test)

    args = argparser.parse_args()
    args.func(args)


#
# Sub-commands
#


def list_info(args):
    """Subcommand to print out metadata of all packages contained in a directory"""
    container_dir = args.dir
    setup_dirs = pydep.setup_py.setup_dirs(container_dir)
    setup_infos = []
    for setup_dir in setup_dirs:
        setup_dict, err = pydep.setup_py.setup_info_dir(setup_dir)
        if err is not None:
            sys.stderr.write('failed due to error: %s\n' % err)
            sys.exit(1)
        setup_infos.append(
            setup_dict_to_json_serializable_dict(setup_dict, rootdir=path.relpath(setup_dir, container_dir)))
    print(json.dumps(setup_infos))


def info(args):
    """Subcommand to print out metadata of package"""
    setup_dict, err = pydep.setup_py.setup_info_dir(args.dir)
    if err is not None:
        sys.stderr.write('failed due to error: %s\n' % err)
        sys.exit(1)
    print(json.dumps(setup_dict_to_json_serializable_dict(setup_dict)))


def dep(args):
    """Subcommand to print out dependencies of project"""
    reqs, err = pydep.req.requirements(args.dir, not args.raw)
    if err is not None:
        sys.stderr.write('failed due to error: %s\n' % err)
        sys.exit(1)
    print(json.dumps(reqs))


def smoke_test(args):
    """Test subcommand that runs pydep on a few popular repositories and prints the results."""
    testcases = [
        ('Flask', 'https://github.com/mitsuhiko/flask.git'),
        ('Graphite, a webapp that depends on Django', 'https://github.com/graphite-project/graphite-web'),
        # TODO: update smoke_test to call setup_dirs/list instead of assuming setup.py exists at the repository root
        # ('Node', 'https://github.com/joyent/node.git'),
    ]
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp()
        for title, cloneURL in testcases:
            print('Downloading and processing %s...' % title)
            subdir = path.splitext(path.basename(cloneURL))[0]
            dir_ = path.join(tmpdir, subdir)
            with open('/dev/null', 'w') as devnull:
                subprocess.call(['git', 'clone', cloneURL, dir_], stdout=devnull, stderr=devnull)

            print('')
            reqs, err = pydep.req.requirements(dir_, True)
            if err is None:
                print('Here is some info about the dependencies of %s' % title)
                if len(reqs) == 0:
                    print('(There were no dependencies found for %s)' % title)
                else:
                    print(json.dumps(reqs, indent=2))
            else:
                print('failed with error: %s' % err)

            print('')
            setup_dict, err = pydep.setup_py.setup_info_dir(dir_)
            if err is None:
                print('Here is the metadata for %s' % title)
                print(json.dumps(setup_dict_to_json_serializable_dict(setup_dict), indent=2))
            else:
                print('failed with error: %s' % err)

    except Exception as e:
        print('failed with exception %s' % str(e))
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir)

#
# Helpers
#


def setup_dict_to_json_serializable_dict(d, **kw):
    return {
        'rootdir': kw['rootdir'] if 'rootdir' in kw else None,
        'project_name': d['name'] if 'name' in d else None,
        'version': d['version'] if 'version' in d else None,
        'repo_url': d['url'] if 'url' in d else None,
        'packages': d['packages'] if 'packages' in d else None,
        'modules': d['py_modules'] if 'py_modules' in d else None,
        'scripts': d['scripts'] if 'scripts' in d else None,
        'author': d['author'] if 'author' in d else None,
        'description': d['description'] if 'description' in d else None,
    }


if __name__ == '__main__':
    main()
