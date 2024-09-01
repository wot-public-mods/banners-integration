# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2024 Andrii Andrushchyshyn

__version__ = "1.3.1"

from .controller import g_instance
from .hooks import *

__all__ = ('init', 'fini')

def init():
	g_instance.init()

def fini():
	g_instance.cleanup()
