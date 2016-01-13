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
        self.preferred = preferred

    def __str__(self):
        return '{0}x{1}, {2}, curr: {3}, pref: {4}'.format(self.width, \
                self.height, self.freq, self.current, self.preferred)

    def cmd_str(self, arg1):
        return '{0}x{1}'.format(self.width, self.height)

    __repr__ = __str__

class Screen(object):
    def __init__(self, name, primary, modes):
        super(Screen, self).__init__()

        self.name = name
        self.primary = primary
        # list of Modes (width, height)
        self.supported_modes = modes

    def is_connected(self):
        return len(self.supported_modes) != 0

    def __str__(self):
        return '{0}, primary: {1}, modes: {2}, conn: {3}'.format(self.name, \
                self.primary, len(self.supported_modes), self.is_connected())

    __repr__ = __str__


def exec_cmd(cmd):
    # throws exception CalledProcessError
    s = sb.check_output(cmd, stderr=sb.STDOUT)
    return s.split('\n')

def parse_xrandr(lines):
    rx = re.compile('^\s+(\d+)x(\d+)\s+((?:\d+\.)?\d+)([* ]?)([+ ]?)')
    rxconn = re.compile(r'\bconnected\b')
    rxdisconn = re.compile(r'\bdisconnected\b')

    sc_name_line = None
    sc_name = None
    width = None
    height = None
    freq = None
    current = False
    preferred = False

    screens = []
    modes = []

    for i in lines:
        if re.search(rxconn, i):
            if sc_name_line:
                sc_name = sc_name_line.split(' ')[0]
                newscreen = Screen(sc_name, 'primary' in sc_name_line, modes)
                screens.append(newscreen)
                modes = []

            sc_name_line = i

        elif re.search(rxdisconn, i):
            if sc_name_line:
                sc_name = sc_name_line.split(' ')[0]
                newscreen = Screen(sc_name, 'primary' in sc_name_line, modes)
                screens.append(newscreen)
                modes = []

            sc_name = i

        else:
            r = re.search(rx, i)
            if r:
                width = r.group(1)
                height = r.group(2)
                freq = r.group(3)
                current = r.group(4).replace(' ', '') == '*'
                preferred = r.group(5).replace(' ', '') == '+'

                newmode = Mode(width, height, freq, current, preferred)
                modes.append(newmode)

    if sc_name:
        screens.append(Screen(sc_name, 'primary' in sc_name_line, modes))

    return screens

def main():
    print("main entry point\n================")
    s = parse_xrandr(exec_cmd('xrandr'))
    for i in s:
        print i
        for j in i.supported_modes:
            print j
        print '-------------------------'

if __name__ == '__main__':
    main()
