pyrandr
=========

A small python xrandr library. It is written as a wrapper around xrandr command line tool.


pyrandrcli
----------

```
usage: pyrandrcli.py [-h] [--output OUTPUT] [--mode MODE | --auto] [--off]
                     [--dry-run] [--primary]
                     [--rotate {normal,left,right,inverted}]
                     [--left-of OUTPUT | --right-of OUTPUT | --above OUTPUT | --below OUTPUT | --same-as OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       Selects an output to reconfigure.
  --mode MODE           Sets a resolution for the selected output
  --auto                Selects default resolution for the output.
  --off                 Disables the output
  --dry-run             Prints the generated cmdline
  --primary             Set the output as primary
  --rotate {normal,left,right,inverted}
                        Rotate the output content in the specified direction

Position the output:
  Use one of these options to position the output relative to the position
  of another output.

  --left-of OUTPUT
  --right-of OUTPUT
  --above OUTPUT
  --below OUTPUT
  --same-as OUTPUT

```

Usage
-----

Have a look at the source of `examples/pyrandrcli` to learn how to use it.
But it basically boils down to this;

```python

import pyrandr as randr

# get connected screens
cs = randr.connected_screens()[0]

# available resolutions as a tuple in the form of (width, height)
reslist = cs.available_resolutions()

cs.set_resolution((1024, 768))
cs.set_as_primary(True)

# rotate output contents by 90 degrees in the clockwise direction
cs.rotate(RotateDirection.Right)

cs.apply_settings()

```

Credits
-------

[Davydov Denis](https://github.com/dadmoscow)
