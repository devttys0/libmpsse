#!/usr/bin/env python

import re
from setuptools import setup
from setuptools.extension import Extension

with open('src/configure', 'r') as fd:
    version = re.search(
        r'PACKAGE_VERSION=\'(.+)\'',
        fd.read(),
        re.MULTILINE).group(1)

with open('docs/README', 'r') as fd:
    readme = fd.read()

setup(
    name='libmpsse',
    version=version,
    description='Library to interface with SPI/I2C via. FTDI',
    log_description=readme,
    author='devttys0',
    url='https://github.com/devttys0/libmpsse/tree/master/docs',
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    package_dir={
        '': 'src'
    },
    py_modules=[
        "mpsse",
        "pylibmpsse"
    ],
    ext_modules=[
        Extension(
            '_pylibmpsse',
            [
                'src/mpsse.c',
                'src/mpsse.i',
                'src/support.c',
                'src/fast.c'
            ],
            libraries=['ftdi']
        )
    ],
)
