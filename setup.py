#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='pyrandr',
    version='0.1',
    description='A small python xrandr application. It is written as a wrapper around xrandr command line tool.',
    long_description=open('README.md').read(),
    author='Cihangir Akturk',
    author_email='cakturk@gmail.com',
    maintainer='Davydov Denis',
    maintainer_email='dadmoscow@gmail.com',
    url='https://github.com/cakturk/pyrandr',
    license='GNU General Public License',
    install_requires=[
        'six',
    ],
    packages=find_packages(),
)
