#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Cihangir Akturk <cihangir.akturk@tubitak.gov.tr>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import pyrandr as randr
import argparse

def setup_arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', help='Selects an output to reconfigure.')

    gr = ap.add_mutually_exclusive_group()
    gr.add_argument('--mode', help='Sets a resolution for the selected output')
    gr.add_argument('--auto', action='store_true',
            help='Selects default resolution for the output.')
    ap.add_argument('--off', action='store_true',
            help='Disables the output')
    ap.add_argument('--dry-run', action='store_true',
            help='Prints the generated cmdline')

    ap.add_argument('--primary', action='store_true',
            help='Set the output as primary')
    ap.add_argument('--rotate', choices=[ 'normal', 'left',
        'right', 'inverted'],
        help='Rotate the output content in the specified direction')

    rot_gr = ap.add_argument_group('Position the output',
            'Use  one  of  these  options  to  position ' \
            'the output relative to the position of another output.')
    gr = rot_gr.add_mutually_exclusive_group()
    gr.add_argument('--left-of', metavar='OUTPUT')
    gr.add_argument('--right-of', metavar='OUTPUT')
    gr.add_argument('--above', metavar='OUTPUT')
    gr.add_argument('--below', metavar='OUTPUT')
    gr.add_argument('--same-as', metavar='OUTPUT')

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
        print(screen.build_cmd())
    else:
        screen.apply_settings()
    sys.exit(0)

def main():
    cs = randr.connected_screens()
    ap = setup_arg_parser()
    args = ap.parse_args()
    if len(sys.argv) == 1:
        for s in cs:
            print(s)
            for m in s.supported_modes:
                print(m)
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
