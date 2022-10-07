__author__ = "Andrii Andrushchyshyn"
__copyright__ = "Copyright 2022, poliroid"
__credits__ = ["Andrii Andrushchyshyn"]
__license__ = "LGPL-3.0-or-later"
__version__ = "1.3.0"
__maintainer__ = "Andrii Andrushchyshyn"
__email__ = "contact@poliroid.me"
__status__ = "Production"

from .controller import g_instance
from .hooks import *

__all__ = ('init', 'fini')

def init():
	g_instance.init()

def fini():
	g_instance.cleanup()
