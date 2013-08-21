from platform import python_implementation
if python_implementation() == 'PyPy':
    raise ImportError('PyPy not supported yet')
else:
    from _nanomsg import *
