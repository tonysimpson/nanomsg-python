from __future__ import division, absolute_import, print_function, unicode_literals

from nanomsg_wrappers import load_wrapper as _load_wrapper
_wrapper = _load_wrapper()

globals().update(_wrapper.__dict__)
