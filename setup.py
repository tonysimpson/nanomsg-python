try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


module1 = Extension('_nanomsg_cpy',
                    sources=['_nanomsg_cpy/wrapper.c'],
                    libraries=['nanomsg'],
                    )


setup(name='nanomsg',
      version='0.1a2',
      packages=['nanomsg', '_nanomsg_ctypes', 'nanomsg_wrappers'],
      ext_modules=[module1])
