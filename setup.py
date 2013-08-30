from __future__ import division, absolute_import, print_function,\
 unicode_literals

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup, Extension
from distutils.core import Extension
from distutils.errors import DistutilsError
from distutils.command.build_ext import build_ext


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


setup(name='nanomsg',
      version='0.1a2',
      packages=['nanomsg', '_nanomsg_ctypes', 'nanomsg_wrappers'],
      ext_modules=[cpy_extension],
      cmdclass = {'build_ext': skippable_build_ext},
)
