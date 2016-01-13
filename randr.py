#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess as sb
import re

class Mode(object):
    """docstring for Mode"""
    def __init__(self, width, height, freq, current, preferred):
        super(Mode, self).__init__()
        self.width = width
        self.height = height
        self.freq = freq
        self.current = current
        self.prefferred = preferred

    def __str__(self):
        return '{0}x{1}'.format(self.width, self.height)

    __repr__ = __str__

class Screen(object):
    def __init__(self):
        super(Screen, self).__init__()

        self.name = None
        # list of Modes (width, height)
        self.supported_modes = []

    def is_connected(self):
        return len(supported_modes) != 0


def exec_cmd(cmd):
    # throws exception CalledProcessError
    s = sb.check_output(cmd, stderr=sb.STDOUT)
    return s.split('\n')

def parse_xrandr(lines):
    rx = re.compile('^\s+(\d+)x(\d+)\s+((?:\d+\.)?\d+)([* ]?)([+ ]?)')
    rxconn = re.compile(r'\bconnected\b')
    rxdisconn = re.compile(r'\bdisconnected\b')

    sc_name = None
    width = None
    height = None
    freq = None
    current = False
    preferred = False
    modes = []

    for i in lines:
        if re.search(rxconn, i):
            sc_name = i.split(' ')[0]
        elif re.search(rxdisconn, i):
            sc_name = i.split(' ')[0]
        else:
            r = re.search(rx, i)
            if r:
                width = r.group(1)
                height = r.group(2)
                freq = r.group(3)
                current = r.group(4).replace(' ', '') == '*'
                #prefferred = r.group(5).replace(' ', '') == '+'
                preferred = r.group(5).replace(' ', '') == '+'
                print width, height, freq, current, preferred
                #print preferred

def main():
    print("main entry point\n================")
    parse_xrandr(exec_cmd('xrandr'))

if __name__ == '__main__':
    main()
