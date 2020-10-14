
import json
import time
import os

import BigWorld
import Keys
import Math

from aih_constants import CTRL_MODE_NAME
from gui.banners_integration._constants import MODEL, ENTITIES_PATH, MODEL_PATH
from gui.banners_integration.utils import byteify, checkKeySet

__all__ = ('Model', 'g_instance', 'keysMapping')

class Model(object):

	@property
	def name(self):
		return self.__name

	@property
	def position(self):
		return self.__pos

	@property
	def direction(self):
		return self.__yrp

	def __init__(self):
		self._model = None
		self._motor = None
		self.__name = None
		self.__data = None
		self.__pos = None
		self.__yrp = None
		self.__changed = False

	def setData(self, name, data):
		self.__name = name
		self.__data = data
		self.__pos = Math.Vector3(data[MODEL.POSITION])
		self.__yrp = Math.Vector3(data[MODEL.DIRECTION])
		self._motor = BigWorld.Servo(Math.Matrix())
		self._model = BigWorld.Model(MODEL_PATH % str(data['model']))
		self._model.addMotor(self._motor)
		self._model.visible = True
		BigWorld.addModel(self._model, BigWorld.player().spaceID)
		self.__update()

	def updateData(self, pos=None, yrp=None):
		self.__changed = True
		if pos is not None:
			self.__pos = pos
		if yrp is not None:
			self.__yrp = yrp
		self.__update()

	def destroy(self):
		if self.__changed:
			with open('%s/%s' % (ENTITIES_PATH, self.__name), 'wb') as fh:
				fh.write(json.dumps(byteify({
					'model': self.__data['model'],
					'geometryName': self.__data['geometryName'],
					MODEL.POSITION: [self.__pos.x, self.__pos.y, self.__pos.z],
					MODEL.DIRECTION: [self.__yrp.x, self.__yrp.y, self.__yrp.z]
				}), indent=4, sort_keys=True))

		if self._model and self._model in BigWorld.models():
			BigWorld.delModel(self._model)
		self._motor = None
		self._model = None
		self.__pos = None
		self.__yrp = None
		self.__data = None

	def getDistance(self, point):
		if not self.__pos:
			return 0
		return (self.__pos - point).length

	def __update(self):
		m = Math.Matrix()
		m.setRotateYPR(self.__yrp)
		m.translation = self.__pos
		self._motor.signal = m

class ModelsController(object):

	def __init__(self):
		self.modelsRaw = []
		self.models = []

	def init(self):
		if not os.path.isdir(ENTITIES_PATH):
			return
		for fileName in os.listdir(ENTITIES_PATH):
			if not fileName.endswith('.json'):
				continue
			with open('%s/%s' % (ENTITIES_PATH, fileName), "rb") as fh:
				self.modelsRaw.append((fileName, byteify(json.load(fh))))

	def cleanup(self):
		while self.models:
			model = self.models.pop()
			model.destroy()
		self.models = []

	def addModel(self, model):
		geometryName = BigWorld.player().arena.arenaType.geometryName
		fileName = '%s_%s.json' % (geometryName, str(int(time.time())))
		cameraPosition = BigWorld.camera().position
		position = [cameraPosition.x, cameraPosition.y, cameraPosition.z]
		direction = [0.0, 0.0, 0.0]
		data = {
			'model': model,
			'geometryName': str(geometryName),
			MODEL.POSITION: position,
			MODEL.DIRECTION: direction
		}
		self.modelsRaw.append((fileName, data))
		model = Model()
		model.setData(fileName, data)
		self.models.append(model)
		with open('%s/%s' % (ENTITIES_PATH, fileName), 'wb') as fh:
			fh.write(json.dumps(byteify(data), indent=4, sort_keys=True))
		return True

	def updateModel(self, moveType, coordinate, moveOffset):
		model = self.__nearModel()
		if not model:
			return False
		if moveType == MODEL.POSITION:
			target = model.position
		elif moveType == MODEL.DIRECTION:
			target = model.direction
		baseValue = 0.02
		if checkKeySet([Keys.KEY_LALT]):
			baseValue = 0.1
		if coordinate == MODEL.X:
			offset = Math.Vector3(baseValue * moveOffset, 0.0, 0.0)
		elif coordinate == MODEL.Y:
			offset = Math.Vector3(0.0, baseValue * moveOffset, 0.0)
		elif coordinate == MODEL.Z:
			offset = Math.Vector3(0.0, 0.0, baseValue * moveOffset)
		target += offset
		if moveType == MODEL.POSITION:
			model.updateData(pos=target)
		elif moveType == MODEL.DIRECTION:
			model.updateData(yrp=target)
		return True

	def delModel(self):
		targetModel = self.__nearModel()
		if not targetModel:
			return
		fileName = targetModel.name
		for idx, model in enumerate(self.models):
			if model.name == fileName:
				self.models.pop(idx)
		for idx, (name, _) in enumerate(self.modelsRaw):
			if name == fileName:
				self.modelsRaw.pop(idx)
		targetModel.destroy()
		os.remove('%s/%s' % (ENTITIES_PATH, fileName))

	def __nearModel(self):
		cameraPosition = BigWorld.camera().position
		distanceTemp = 99999
		targetModel = None
		for model in self.models:
			modelDistance = model.getDistance(cameraPosition)
			if modelDistance < distanceTemp:
				distanceTemp = modelDistance
				targetModel = model
		return targetModel

	def getModelPosition(self, name):
		for model in self.models:
			if model.name == name:
				return model.position

g_instance = ModelsController()

def activateFreeCam():
	inputHandler = getattr(BigWorld.player(), 'inputHandler', None)
	if inputHandler and inputHandler.ctrlModeName == CTRL_MODE_NAME.ARCADE:
		inputHandler.onControlModeChanged(CTRL_MODE_NAME.VIDEO, prevModeName=inputHandler.ctrlModeName,
											camMatrix=BigWorld.camera().matrix)

keysMapping = [
	[[Keys.KEY_LCONTROL, Keys.KEY_LALT, Keys.KEY_1], lambda: g_instance.addModel("banner_1")],
	[[Keys.KEY_LCONTROL, Keys.KEY_LALT, Keys.KEY_2], lambda: g_instance.addModel("banner_2")],
	[[Keys.KEY_LCONTROL, Keys.KEY_LALT, Keys.KEY_3], lambda: g_instance.addModel("banner_3")],
	[[Keys.KEY_LCONTROL, Keys.KEY_LALT, Keys.KEY_4], lambda: g_instance.addModel("banner_4")],

	[[Keys.KEY_LCONTROL, Keys.KEY_F1], activateFreeCam],

	[[Keys.KEY_LCONTROL, Keys.KEY_DELETE], g_instance.delModel],

	[[Keys.KEY_LCONTROL, Keys.KEY_Z, Keys.KEY_UPARROW], lambda: g_instance.updateModel(MODEL.POSITION, MODEL.X, 1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_Z, Keys.KEY_DOWNARROW], lambda: g_instance.updateModel(MODEL.POSITION, MODEL.X, -1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_X, Keys.KEY_UPARROW], lambda: g_instance.updateModel(MODEL.POSITION, MODEL.Y, 1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_X, Keys.KEY_DOWNARROW], lambda: g_instance.updateModel(MODEL.POSITION, MODEL.Y, -1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_C, Keys.KEY_UPARROW], lambda: g_instance.updateModel(MODEL.POSITION, MODEL.Z, 1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_C, Keys.KEY_DOWNARROW], lambda: g_instance.updateModel(MODEL.POSITION, MODEL.Z, -1)],

	[[Keys.KEY_LCONTROL, Keys.KEY_A, Keys.KEY_UPARROW], lambda: g_instance.updateModel(MODEL.DIRECTION, MODEL.X, 1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_A, Keys.KEY_DOWNARROW], lambda: g_instance.updateModel(MODEL.DIRECTION, MODEL.X, -1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_S, Keys.KEY_UPARROW], lambda: g_instance.updateModel(MODEL.DIRECTION, MODEL.Y, 1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_S, Keys.KEY_DOWNARROW], lambda: g_instance.updateModel(MODEL.DIRECTION, MODEL.Y, -1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_D, Keys.KEY_UPARROW], lambda: g_instance.updateModel(MODEL.DIRECTION, MODEL.Z, 1)],
	[[Keys.KEY_LCONTROL, Keys.KEY_D, Keys.KEY_DOWNARROW], lambda: g_instance.updateModel(MODEL.DIRECTION, MODEL.Z, -1)],
]
