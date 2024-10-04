# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2024 Andrii Andrushchyshyn

import json
import os

import BigWorld
import Math

from ._constants import DATA_PATH, MODEL_NAME_MASK
from .utils import byteify, vfs_file_exist, pack_vector
from .state import battle_state

class Model(object):

	@property
	def file_name(self):
		return self._file_name

	@property
	def position(self):
		return self._position

	@position.setter
	def position(self, value):
		self.__changed = False
		self._position = value
		self._update()

	@property
	def rotation(self):
		return self._rotation

	@rotation.setter
	def rotation(self, value):
		self.__changed = False
		self._rotation = value
		self._update()

	def __init__(self):
		self._position = None
		self._rotation = None
		self._file_name = None

		self._model = None
		self._motor = None

		self.__raw = None
		self.__changed = False

	def init(self, file_name, data):

		model_path = MODEL_NAME_MASK % str(data['model'])

		if not vfs_file_exist(model_path):
			return False

		self._position = Math.Vector3(data['position'])
		self._rotation = Math.Vector3(data['rotation'])
		self._file_name = file_name
		self.__raw = data

		self._model = BigWorld.Model(model_path)
		self._model.visible = True
		self._motor = BigWorld.Servo(Math.Matrix())
		self._model.addMotor(self._motor)
		BigWorld.addModel(self._model, BigWorld.player().spaceID)

		self._update()

		return True

	def destroy(self):

		if self.__changed:
			self.dump()

		if self._model and self._model in BigWorld.models():
			BigWorld.delModel(self._model)

		self._motor = None
		self._model = None
		self._position = None
		self._rotation = None
		self.__raw = None

	def _update(self):
		#m = Math.Matrix()
		#m.setRotateYPR(self._rotation)
		#m.translation = self._position
		m = Math.createRTMatrix(self._rotation, self._position)
		self._motor.signal = m

	def dump(self):
		self.__raw.update({
			'position': pack_vector(self._position),
			'rotation': pack_vector(self._rotation)
		})
		with open('%s/%s' % (DATA_PATH, self._file_name), 'wb') as fh:
			fh.write(json.dumps(byteify(self.__raw)))

class ModelsController:

	def __init__(self):
		self.entities = []
		self.models = []
		self._root_model = None

	def init(self):
		if not os.path.isdir(DATA_PATH):
			return
		battle_state.onBattleLoaded += self.onBattleLoaded
		battle_state.onBattleClosed += self.onBattleClosed
		for file_name in os.listdir(DATA_PATH):
			if not file_name.endswith('.json'):
				continue
			with open('%s/%s' % (DATA_PATH, file_name), 'rb') as fh:
				self.entities.append((file_name, byteify(json.load(fh))))

	def onBattleLoaded(self):
		geometry = BigWorld.player().arena.arenaType.geometryName
		for file_name, data in self.entities:
			if data['geometry'] != str(geometry):
				continue
			model = Model()
			if model.init(file_name, data):
				self.models.append(model)

	def onBattleClosed(self):
		while self.models:
			model = self.models.pop()
			model.destroy()
		self.models = []

	def fini(self):
		self.onBattleClosed()

g_instance = ModelsController()
