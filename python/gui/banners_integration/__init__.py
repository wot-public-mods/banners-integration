__author__ = "Andruschyshyn Andrey"
__copyright__ = "Copyright 2020, poliroid"
__credits__ = ["Andruschyshyn Andrey"]
__license__ = "CC BY-NC-SA 4.0"
__version__ = "1.2.4"
__maintainer__ = "Andruschyshyn Andrey"
__email__ = "p0lir0id@yandex.ru"
__status__ = "Production"

from gui.banners_integration.controller import g_instance
from gui.banners_integration.hooks import *

__all__ = ('init', 'fini')

def init():
	g_instance.init()

def fini():
	g_instance.cleanup()
