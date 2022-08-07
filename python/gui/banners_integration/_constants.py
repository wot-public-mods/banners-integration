
import os

__all__ = ('IS_DEV', 'ENTITIES_PATH', 'MODEL', 'MODEL_PATH')

IS_DEV = os.path.isfile('./banners-integration.dev')

ENTITIES_PATH = './mods/resources/banners.integration'

MODEL_PATH = 'content/mods/banners.integration/%s.model'

class MODEL:
	POSITION = 'position'
	DIRECTION = 'direction'
	X = 'x'
	Y = 'y'
	Z = 'z'
