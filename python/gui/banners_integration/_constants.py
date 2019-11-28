
import os
import sys

__all__ = ('IS_DEV', 'ENTITIES_PATH', 'MODEL', 'MODEL_PATH')

# Client installation folder (same to './../' but does not depend on the working directory)
CLIENT_ROOT = os.path.sep.join(sys.executable.split(os.path.sep)[:-2])
IS_DEV = os.path.isfile('%s/banners-integration.dev' % CLIENT_ROOT)

ENTITIES_PATH = '%s/mods/resources/banners.integration' % CLIENT_ROOT

MODEL_PATH = 'content/mods/banners.integration/%s.model'

class MODEL:
	POSITION = 'position'
	DIRECTION = 'direction'
	X = 'x'
	Y = 'y'
	Z = 'z'
