from setuptools import setup, Extension

module1 = Extension('_nanomsg',
                    sources = ['_nanomsg_cpy/wrapper.c'],
                    libraries=['nanomsg'])

setup (name = 'nanomsg',
       version = '0.1a1',
       packages=['nanomsg'],
       ext_modules = [module1])
