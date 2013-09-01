from __future__ import division, absolute_import, print_function,\
 unicode_literals

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup, Extension
from distutils.core import Extension
from distutils.errors import DistutilsError
from distutils.command.build_ext import build_ext


with open(os.path.join('nanomsg','version.py')) as f:
    exec(f.read())


class skippable_build_ext(build_ext):
    def run(self):
        try:
            build_ext.run(self)
        except Exception as e:
            print()
            print("=" * 79)
            print("WARNING : CPython API extension could not be built.")
            print()
            print("Exception was : %r" % (e,))
            print()
            print(
                "If you need the extensions (they may be faster than "
                "alternative on some"
            )
            print(" platforms) check you have a compiler configured with all"
                  " the necessary")
            print(" headers and libraries.")
            print("=" * 79)
            print()


cpy_extension = Extension(str('_nanomsg_cpy'),
                    sources=[str('_nanomsg_cpy/wrapper.c')],
                    libraries=[str('nanomsg')],
                    )


setup(
    name='nanomsg',
    version=__version__,
    packages=['nanomsg', '_nanomsg_ctypes', 'nanomsg_wrappers'],
    ext_modules=[cpy_extension],
    cmdclass = {'build_ext': skippable_build_ext},

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
)
