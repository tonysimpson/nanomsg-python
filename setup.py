from __future__ import division, absolute_import, print_function, unicode_literals

import os
import sys
from setuptools import setup
from distutils.core import Extension
from distutils.command.build_ext import build_ext


with open(os.path.join('nanomsg','version.py')) as f:
    exec(f.read())

try:
    import ctypes
    if sys.platform in ('win32', 'cygwin'):
        _lib = ctypes.windll.nanoconfig
    elif sys.platform == 'darwin':
        _lib = ctypes.cdll.LoadLibrary('libnanoconfig.dylib')
    else:
        _lib = ctypes.cdll.LoadLibrary('libnanoconfig.so')
except OSError:
    # Building without nanoconfig
    cpy_extension = Extension(str('_nanomsg_cpy'),
                        sources=[str('_nanomsg_cpy/wrapper.c')],
                        libraries=[str('nanomsg')],
                        include_dirs=['/usr/local/include', ],
                        )
else:
    # Building with nanoconfig
    cpy_extension = Extension(str('_nanomsg_cpy'),
                        define_macros=[('WITH_NANOCONFIG', '1')],
                        sources=[str('_nanomsg_cpy/wrapper.c')],
                        libraries=[str('nanomsg'), str('nanoconfig')],
                        include_dirs=['/usr/local/include', ],
                        )
install_requires = []

try:
    import importlib
except ImportError:
    install_requires.append('importlib')


setup(
    name='nanomsg',
    version=__version__,
    packages=[str('nanomsg'), str('_nanomsg_ctypes'), str('nanomsg_wrappers')],
    ext_modules=[cpy_extension],
    install_requires=install_requires,
    description='Python library for nanomsg.',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
    author='Tony Simpson',
    author_email='agjasimpson@gmail.com',
    url='https://github.com/tonysimpson/nanomsg-python',
    keywords=['nanomsg', 'driver'],
    license='MIT',
    test_suite="tests",
)
