nanomsg-python
==============

nanomsg wrapper for CPython and Pypy (via cffi)

## Prerequirements

Build and install nanomsg from source: https://github.com/250bpm/nanomsg

## Installation

NOTE: maybe need set ```export LD_LIBRARY_PATH=/usr/local/lib``` in your environment.

    git clone git@github.com:tonysimpson/nanomsg-python.git
    cd nanomsg-python
    (sudo)python setup.py develop
    (sudo)python setup.py install

## Runnning tests

    py.test tests/