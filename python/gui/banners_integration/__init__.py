# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2025 Andrii Andrushchyshyn

from .controller import g_instance
from .hooks import *

def init():
	g_instance.init()

def fini():
	g_instance.fini()
