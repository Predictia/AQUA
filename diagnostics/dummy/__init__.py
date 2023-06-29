"""DUMMY module"""

from .dummy_class_readerwrapper import DummyDiagnosticWrapper
from .dummy_class_timeband import DummyDiagnostic
from .dummy_func import dummy_func

__version__ = '0.0.1'

__all__ = ["DummyDiagnostic", "DummyDiagnosticWrapper", "dummy_func"]
