#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA main command line
'''

import argparse

def init(args):
    print('running the AQUA init')

def catalogadd():
    print('adding the AQUA catalog')

def main():
    parser = argparse.ArgumentParser(description='AQUA command line tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]')
    
    init_parser = subparsers.add_parser("init")
    catalogadd_parser = subparsers.add_parser("catalog-add")

    init_parser.add_argument('-p', '--path', type=str,
                help='Path where to install AQUA')

    args = parser.parse_args()

    if args.command == 'init':
        init(args)
    elif args.command == 'run':
        catalogadd(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
