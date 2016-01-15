#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import pyrandr as randr
import argparse

def setup_arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output')

    gr = ap.add_mutually_exclusive_group()
    gr.add_argument('--mode')
    gr.add_argument('--auto', action='store_true')
    ap.add_argument('--off', action='store_true')
    ap.add_argument('--dry-run', action='store_true')

    ap.add_argument('--primary', action='store_true')
    ap.add_argument('--rotate', choices=[ 'normal', 'left',
        'right', 'inverted'])

    gr = ap.add_mutually_exclusive_group()
    gr.add_argument('--left-of')
    gr.add_argument('--right-of')
    gr.add_argument('--above')
    gr.add_argument('--below')
    gr.add_argument('--same-as')

    return ap

def die(msg):
    sys.stderr.write(msg)
    sys.exit(127)

def find_output_or_die(outputname, screens):
    for s in screens:
        if outputname == s.name:
            return s
    die('\ninvalid --output: {}\n'.format(outputname))

def execute(screen, dry_run=False):
    if dry_run:
        print screen.build_cmd()
    else:
        screen.apply_settings()
    sys.exit(0)

def main():
    cs = randr.connected_screens()
    ap = setup_arg_parser()
    args = ap.parse_args()
    if len(sys.argv) == 1:
        for s in cs:
            print s
            for m in s.supported_modes:
                print m
        sys.exit(0)

    if not args.output:
        ap.print_help()
        sys.stderr.write('\n--output is required\n\n')
    sc = find_output_or_die(args.output, cs)

    if args.off:
        sc.set_enabled(not args.off)
        execute(sc, args.dry_run)

    if args.mode:
        pair = args.mode.split('x')
        try:
            width = int(pair[0])
            height = int(pair[1])
            sc.set_resolution((width, height))
        except Exception as e:
            die('\nInvalid mode: {}\n'.format(args.mode))

    if args.primary:
        sc.set_as_primary(args.primary)
    if args.rotate:
        sc.rotate(randr.str_to_rot(args.rotate))
    relation = None
    relative_to = None
    if args.left_of:
        relation = '--left-of'
        relative_to = args.left_of
    elif args.right_of:
        relation = '--right-of'
        relative_to = args.right_of
    elif args.above:
        relation = '--above'
        relative_to = args.above
    elif args.below:
        relation = '--below'
        relative_to = args.below
    if relation:
        sc.set_position(randr.str_to_pos(relation), relative_to)
    execute(sc, args.dry_run)

if __name__ == '__main__':
    main()
