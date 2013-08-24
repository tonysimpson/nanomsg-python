try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


library_dirs = ["/usr/local/lib"]
include_dirs = ["/usr/local/include/nanomsg"]

module1 = Extension('nanomsg._nanomsg',
                    sources=['_nanomsg_cpy/wrapper.c'],
                    libraries=['nanomsg'],
                    include_dirs=include_dirs,
                    library_dirs=library_dirs
                    )


setup(name='nanomsg',
      version='0.1a1',
      packages=['nanomsg'],
      ext_modules=[module1])
