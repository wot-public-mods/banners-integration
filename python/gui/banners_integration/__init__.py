# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2024 Andrii Andrushchyshyn

__version__ = '2.0.00'

from .controller import g_instance
from .hooks import *

def init():
	g_instance.init()

def fini():
	g_instance.fini()
