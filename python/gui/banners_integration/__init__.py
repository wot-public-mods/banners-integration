__author__ = "Andruschyshyn Andrey"
__copyright__ = "Copyright 2019, Wargaming"
__credits__ = ["Andruschyshyn Andrey"]
__license__ = "CC BY-NC-SA 4.0"
__version__ = "1.2.2"
__maintainer__ = "Andruschyshyn Andrey"
__email__ = "prn.a_andruschyshyn@wargaming.net"
__status__ = "Production"

from gui.banners_integration.controller import g_instance
from gui.banners_integration.hooks import *

__all__ = ('init', 'fini')

def init():
	g_instance.init()

def fini():
	g_instance.clean()
