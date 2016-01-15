#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess as sb

class Mode(object):
    """docstring for Mode"""
    def __init__(self, width, height, freq, current, preferred):
        super(Mode, self).__init__()
        self.width = width
        self.height = height
        self.freq = freq
        self.current = current
        self.preferred = preferred

    def get_resolution(self):
        return (self.width, self.height)

    def __str__(self):
        return '{0}x{1}, {2}, curr: {3}, pref: {4}'.format(self.width, \
                self.height, self.freq, self.current, self.preferred)

    def cmd_str(self, arg1):
        return '{0}x{1}'.format(self.width, self.height)

    __repr__ = __str__

class ScreenSettings(object):
    """docstring for ScreenSettings"""
    def __init__(self):
        super(ScreenSettings, self).__init__()
        self.reset()

    def reset(self):
        self.resolution = None
        self.is_primary = False
        self.is_enabled = True
        self.rotation = None
        self.position = None
        self.dirty = False

class Screen(object):
    def __init__(self, name, primary, rot, modes):
        super(Screen, self).__init__()

        self.name = name
        self.primary = primary

        # dirty hack
        self.rotation = None
        for r in modes:
            if r.current:
                self.rotation = rot
                self.curr_mode = r
                break

        # list of Modes (width, height)
        self.supported_modes = modes

        self.set = ScreenSettings()
        self.set.is_enabled = self.is_enabled()

    def is_connected(self):
        return len(self.supported_modes) != 0

    def is_enabled(self):
        for m in self.supported_modes:
            if m.current:
                return True
        return False

    def get_available_resolutions(self):
        return [(r.width, r.height) for r in self.supported_modes]

    def check_resolution(self, newres):
        if newres not in self.get_available_resolutions():
            raise ValueError('Requested resolution is not supported', newres)

    def set_resolution(self, newres):
        """Sets the resolution of this screen to the supplied
           @newres parameter.

        :newres: must be a tuple in the form (width, height)

        """
        if not self.is_enabled():
            raise ValueError('The Screen is off')

        self.check_resolution(newres)
        self.set.resolution = newres

    def set_as_primary(self,  is_primary):
        """Set this monitor as primary

        :is_primary: bool

        """
        self.set.is_primary = is_primary

    def set_enabled(self, enable):
        """Enable or disable the output

        :enable: bool

        """
        self.set.is_enabled = enable

    def rotate(self, direction):
        """Rotate the output in the specified direction

        :direction: one of (normal, left, right, inverted)

        """
        self.set.rotation = direction

    def set_position(self, relation, relative_to):
        """Position the output relative to the position
        of another output.

        :relation: TODO
        :relative_to: output name (LVDS1, HDMI eg.)
        """
        self.set.position = (relation, relative_to)

    def apply_settings(self):
        if not self.name:
            raise ValueError('Cannot apply settings without screen name', \
                             self.name)
        if self.set.resolution:
            self.check_resolution(self.set.resolution)

        has_changed = False

        cmd = ['xrandr', '--output', self.name]

        # set resolution
        if self.curr_mode.get_resolution() == self.set.resolution \
                or not self.set.resolution:
            cmd.append('--auto')
        else:
            res = self.set.resolution
            cmd.extend(['--mode', '{0}x{1}'.format(res[0], res[1])])
            has_changed = True

        # Check if this screen is already primary
        if not self.primary and self.set.is_primary:
            cmd.append('--primary')
            has_changed = True

        if self.set.rotation and self.set.rotation is not self.rotation:
            rot = rot_to_str(self.set.rotation)
            if not rot:
                raise ValueError('Invalid rotation value', \
                                 rot, self.set.rotation)
            cmd.extend(['--rotate', rot])
            has_changed = True

        if self.set.position:
            rel, rel_to = self.set.position
            rel = pos_to_str(rel)
            cmd.extend([rel, rel_to])
            has_changed = True

        if self.is_enabled() and not self.set.is_enabled:
            if has_changed:
                raise Exception('--off: this option cannot be combined ' \
                                'with other options')
            cmd.append('--off')
            has_changed = True

    def __str__(self):
        return '{0}, primary: {1}, modes: {2}, conn: {3}, rot: {4}, '\
                'enabled: {5}'.format(self.name, self.primary, \
                len(self.supported_modes), self.is_connected(), \
                rot_to_str(self.rotation), self.is_enabled())

    __repr__ = __str__

class RotateDirection(object):
    Normal, Left, Inverted, Right = range(1, 5)
    valtoname = {Normal:'normal', Left:'left', Inverted:'inverted', \
            Right:'right'}
    nametoval = dict((v, k) for k, v in valtoname.iteritems())

def rot_to_str(rot):
    if rot in RotateDirection.valtoname:
        return RotateDirection.valtoname[rot]
    return None

def str_to_rot(s):
    if s in RotateDirection.nametoval:
        return RotateDirection.nametoval[s]
    return RotateDirection.Normal

class PostitonType(object):
    LeftOf, RightOf, Above, Below, SameAs = range(1, 6)
    valtoname = {LeftOf:'--left-of', RightOf:'--right-of', Above:'--above', \
                 Below:'--below', SameAs:'--same-as'}
    nametoval = dict((v, k) for k, v in valtoname.iteritems())

def pos_to_str(n):
    return PostitonType.valtoname[n]

def str_to_pos(s):
    return PostitonType.nametoval[s]

def exec_cmd(cmd):
    # throws exception CalledProcessError
    s = sb.check_output(cmd, stderr=sb.STDOUT)
    return s.split('\n')

def create_screen(name_str, modes):
    rot = None
    sc_name = name_str.split(' ')[0]

    # if connected
    if modes:
        fr = name_str.split(' ')
        if len(fr) > 2:
            rot = str_to_rot(name_str.split(' ')[3])

    return Screen(sc_name, 'primary' in name_str, rot, modes)

def parse_xrandr(lines):
    import re
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
        if re.search(rxconn, i) or re.search(rxdisconn, i):
            if sc_name_line:
                newscreen = create_screen(sc_name_line, modes)
                screens.append(newscreen)
                modes = []

            sc_name_line = i

        else:
            r = re.search(rx, i)
            if r:
                width = int(r.group(1))
                height = int(r.group(2))
                freq = float(r.group(3))
                current = r.group(4).replace(' ', '') == '*'
                preferred = r.group(5).replace(' ', '') == '+'

                newmode = Mode(width, height, freq, current, preferred)
                modes.append(newmode)

    if sc_name_line:
        screens.append(create_screen(sc_name_line, modes))

    return screens

def get_connected_screens():
    """Get connected screens
    """
    return [s for s in parse_xrandr(exec_cmd('xrandr')) if s.is_connected()]

def get_enabled_screens():
    return [s for s in get_connected_screens() if s.is_enabled()]

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
