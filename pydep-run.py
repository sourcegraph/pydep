#!/usr/bin/env python

import sys
import json
import argparse
import pydep.req

from os import system, path
import subprocess
import tempfile
import shutil

def main():
    # Parse args
    argparser = argparse.ArgumentParser(description='pydep is simple command line tool that tells you about package dependency metadata in Python')
    subparsers = argparser.add_subparsers()
    depparser = subparsers.add_parser('dep', help='print the dependencies of a python project in JSON')
    depparser.add_argument('--raw', action='store_true', help='If true, pydep will not try to resolve dependencies to VCS URLs')
    depparser.add_argument('dir', help='path to root directory of project code')
    depparser.set_defaults(func=dep)
    smokeparser = subparsers.add_parser('demo', help='run pydep against some popular repositories, printing out dependency information about each')
    smokeparser.set_defaults(func=smoke_test)

    args = argparser.parse_args()
    args.func(args)

def dep(args):
    reqs, err = pydep.req.requirements(args.dir, not args.raw)
    if err is not None:
        sys.stderr.write('failed due to error %s' % err)
        sys.exit(1)
    print json.dumps(reqs)

def smoke_test(args):
    testcases = [
        ('Flask', 'https://github.com/mitsuhiko/flask.git'),
        ('Graphite, a webapp that depends on Django', 'https://github.com/graphite-project/graphite-web'),
    ]
    try:
        tmpdir = tempfile.mkdtemp()
        for title, cloneURL in testcases:
            print 'Downloading and processing %s...' % title
            subdir = path.splitext(path.basename(cloneURL))[0]
            dir_ = path.join(tmpdir, subdir)
            with open('/dev/null', 'w') as devnull:
                subprocess.call(['git', 'clone', cloneURL, dir_], stdout=devnull, stderr=devnull)
            reqs, err = pydep.req.requirements(dir_, True)
            if err is None:
                print 'Here is some info about the dependencies of %s' % title
                if len(reqs) == 0:
                    print '(There were no dependencies found for %s)' % title
                else:
                    print json.dumps(reqs, indent=2)
            else:
                print 'failed with error %s' % err
    except Exception as e:
        print 'failed with exception %s' % str(e)
    finally:
        shutil.rmtree(tmpdir)

if __name__ == '__main__':
    main()
