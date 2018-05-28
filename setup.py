from __future__ import division, absolute_import, print_function, unicode_literals

import os
import platform
import sys
from setuptools import setup
from distutils.core import Extension
from distutils.command.build_ext import build_ext


with open(os.path.join('nanomsg','version.py')) as f:
    exec(f.read())


libraries = [str('nanomsg')]
# add additional necessary library/include path info if we're on Windows
if sys.platform in ("win32", "cygwin"):
    libraries.extend([str('ws2_32'), str('advapi32'), str('mswsock')])
    # nanomsg installs to different directory based on architecture
    arch = platform.architecture()[0]
    if arch == "64bit":
        include_dirs=[r'C:\Program Files\nanomsg\include',]
    else:
        include_dirs=[r'C:\Program Files (x86)\nanomsg\include',]
else:
    include_dirs = None

try:
    import ctypes
    if sys.platform in ('win32', 'cygwin'):
        _lib = ctypes.windll.nanoconfig
    elif sys.platform == 'darwin':
        _lib = ctypes.cdll.LoadLibrary('libnanoconfig.dylib')
    else:
        _lib = ctypes.cdll.LoadLibrary('libnanoconfig.so')
except OSError:
    # Building without nanoconfig; need to turn NN_STATIC_LIB on
    define_macros = [('NN_STATIC_LIB','ON')]
else:
    # Building with nanoconfig
    libraries.append(str('nanoconfig'))
    define_macros = [('WITH_NANOCONFIG', '1')]

cpy_extension = Extension(str('_nanomsg_cpy'),
                    define_macros=define_macros,
                    sources=[str('_nanomsg_cpy/wrapper.c')],
                    libraries=libraries,
                    include_dirs=include_dirs,
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
