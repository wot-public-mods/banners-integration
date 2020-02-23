
import os

__all__ = ('IS_DEV', 'ENTITIES_PATH', 'MODEL', 'MODEL_PATH')

CLIENT_ROOT = '.'
IS_DEV = os.path.isfile('%s/banners-integration.dev' % CLIENT_ROOT)

ENTITIES_PATH = '%s/mods/resources/banners.integration' % CLIENT_ROOT

MODEL_PATH = 'content/mods/banners.integration/%s.model'

class MODEL:
	POSITION = 'position'
	DIRECTION = 'direction'
	X = 'x'
	Y = 'y'
	Z = 'z'
