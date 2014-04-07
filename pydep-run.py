#!/usr/bin/env python

import sys
import json
import argparse
import pydep.metadata

def parse_args():
    args = argparse.ArgumentParser(description='pydep is simple command line tool that will print the dependencies of a python project in JSON')
    args.add_argument('--raw', action='store_true', help='If true, pydep will not try to resolve dependencies to VCS URLs')
    args.add_argument('dir', help='path to root directory of project code')
    return args.parse_args()

def main():
    args = parse_args()
    if args.raw:
        reqs, err = pydep.metadata.raw_requirements(args.dir)
    else:
        reqs, err = pydep.metadata.resolved_requirements(args.dir)
    if err is not None:
        sys.stderr.write('failed due to error %s' % err)
        sys.exit(1)
    print json.dumps(reqs)

if __name__ == '__main__':
    main()
