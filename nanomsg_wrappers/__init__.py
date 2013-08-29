from platform import python_implementation
import pkgutil
import importlib
import warnings

_choice = None

def set_wrapper_choice(name):
    global _choice
    _choice = name

def load_wrapper():
    if _choice is not None:
        return importlib.import_module('_nanomsg_' + _choice)
    if python_implementation() == 'CPython':
        try:
            return importlib.import_module('_nanomsg_cpy')
        except ImportError:
            warnings.warn("CPython wrapper could not be imported falling back "
                          "to slower ctypes wrapper!")
    return importlib.import_module('_nanomsg_ctypes')

def list_wrappers():
    return [module_name.split('_',2)[-1] for _, module_name, _ in
     pkgutil.iter_modules() if module_name.startswith('_nanomsg_')]
