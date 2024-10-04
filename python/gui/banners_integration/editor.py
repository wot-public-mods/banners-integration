# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2024 Andrii Andrushchyshyn

import BigWorld
import Math
import GUI
import DebugDrawer
import os
import uuid
import time
import uuid
import Keys

from aih_constants import CTRL_MODE_NAME
from AvatarInputHandler import cameras
from frameworks.wulf import WindowLayer
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control import avatar_getter
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
from gui.Scaleform.framework.entities.DisposableEntity import EntityState
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.managers.cursor_mgr import CursorManager
from gui.shared.personality import ServicesLocator
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

from ._constants import IS_EDITOR, DATA_PATH, DATA_VERSION, MODEL_NAME_MASK
from .controller import g_instance, Model
from .state import battle_state
from .utils import vfs_file_exist

__all__ = ('editor_ctrl', )

class AXIS:
	X = 0
	Y = 1
	Z = 2
	ALL = (X, Y, Z)

OFFSETS = {
	AXIS.X: ((-100, 0.0, 0.0), (100.0, 0.0, 0.0)),
	AXIS.Y: ((0.0, -100, 0.0), (0.0, 100.0, 0.0)),
	AXIS.Z: ((0.0, 0.0, -100), (0.0, 0.0, 100.0))
}

ACTIVATION_DISTANCE = 2.0

COLORS = {
	AXIS.X: 0xFF0000,
	AXIS.Y: 0x0000FF,
	AXIS.Z: 0x00FF00,
}

EPSILONE = 2.2204e-16

MODEL_HOTKEYS = {
	Keys.KEY_1: 'banner_1',
	Keys.KEY_2: 'banner_2',
	Keys.KEY_3: 'banner_3',
	Keys.KEY_4: 'banner_4'
}

def debug_draw_line(dd, colour, pointA, pointB):
	if not dd:
		dd = DebugDrawer.DebugDrawer()
	dd.line().colour(colour).points([pointA, pointB])

def debug_draw_point(dd, colour, point, size):
	if not dd:
		dd = DebugDrawer.DebugDrawer()
	dd.sphere().colour(colour).aabb(
		point - Math.Vector3(size, size, size),
		point + Math.Vector3(size, size, size)
	)

class EditorAxis(object):

	def __init__(self, axis=None, point=None, distance=None):
		super(EditorAxis, self).__init__()
		self.index = axis or AXIS.X
		self.point = point or Math.Vector3(0, 0, 0)
		self.distance = distance or 0.0

	def update(self, data):
		point_on_axis, _, distance = data
		self.point = point_on_axis
		self.distance = distance

	@property
	def color(self):
		return COLORS[self.index]

	@property
	def offsets(self):
		return OFFSETS[self.index]

	def __repr__(self):
		return str(self)

	def __str__(self):
		return '<EditorAxis index=%s, distance=%s>' % (self.index, self.distance)

class InteractiveEditor:

	appLoader = dependency.descriptor(IAppLoader)

	def __init__(self, model):

		self._model = model
		self._src_position = None
		self._src_rotation = None

		self.__terminated = False
		self.__axes = {axis: EditorAxis(axis) for axis in AXIS.ALL}
		self.__active = False
		self.__available = False
		self.__axis = None
		self.__delta = 0.0
		self.__closest = None
		self.__forced_flags = None

		self._callbackID = BigWorld.callback(.0, self.update)

	def destroy(self):
		self.__terminated = True
		if self._callbackID:
			BigWorld.cancelCallback(self._callbackID)
		self._callbackID = None

	def update(self):

		if self.__terminated:
			return

		self._callbackID = BigWorld.callback(.0, self.update)

		dd = DebugDrawer.DebugDrawer()

		x, y = GUI.mcursor().position
		direction, mouse_start = cameras.getWorldRayAndPoint(x, y)
		mouse_end = mouse_start + direction.scale(1000.0)

		# draw axes lines
		for axis in self.__axes.values():
			_min, _max = axis.offsets
			_min, _max = self._model.position + _min, self._model.position + _max
			data = self.shortest_line_data(_min, _max, mouse_start, mouse_end)
			if not data:
				continue
			axis.update(data)
			debug_draw_line(dd, axis.color, _min, _max)

		self.__closest = min(self.__axes.values(), key=lambda x: x.distance)
		self.__available = self.__closest.distance < ACTIVATION_DISTANCE

		# draw closets points
		for axis in self.__axes.values():
			if self.__active and axis == self.__axis:
				debug_draw_point(dd, axis.color, axis.point, 0.5)
			elif axis == self.__closest and self.__available:
				debug_draw_point(dd, axis.color, axis.point, 0.5)
			else:
				debug_draw_point(dd, axis.color, axis.point, 0.2)

		# update mouse
		app = self.appLoader.getDefBattleApp()
		if self.__active:
			app.cursorMgr.setCursorForced(CursorManager.DRAG_CLOSE)
		elif self.__available:
			app.cursorMgr.setCursorForced(CursorManager.DRAG_OPEN)
		else:
			app.cursorMgr.setCursorForced(CursorManager.ARROW)

		if not self.__active:
			return

		# update model
		axis_index = self.__axis.index
		draging_point = self.__axis.point
		# update position
		if not BigWorld.isKeyDown(Keys.KEY_LALT):
			position = Math.Vector3(self._src_position)
			position[axis_index] = draging_point[axis_index] + self.__delta
			self._model.position = position
		# update rotation
		else:
			dragging_delta = (draging_point - self._model.position).length
			if draging_point[axis_index] > self._model.position[axis_index]:
				dragging_delta = -dragging_delta
			rotation = Math.Vector3(self._src_rotation)
			rotation[axis_index] += (dragging_delta - self.__delta) / 20.0
			self._model.rotation = rotation

	def handleKeyEvent(self, event):

		if not BigWorld.isKeyDown(Keys.KEY_LCONTROL):
			return False

		if not event.key == Keys.KEY_LEFTMOUSE:
			return False

		if event.isKeyDown():
			if not self.__active and self.__available:
				self._src_position = Math.Vector3(self._model.position)
				self._src_rotation = Math.Vector3(self._model.rotation)
				self.__axis = self.__closest
				self.__delta = (self.__closest.point - self._model.position).length
				axis_index = self.__axis.index
				if self.__closest.point[axis_index] > self._model.position[axis_index]:
					self.__delta = -self.__delta
				self.__forced_flags = avatar_getter.getForcedGuiControlModeFlags()
				avatar_getter.setForcedGuiControlMode(True, cursorVisible=True, enableAiming=True)
				self.__active = True
				return True

		if not event.isKeyDown() and self.__active:
			self.__active = False
			try:
				if self.__forced_flags:
					BigWorld.player().setForcedGuiControlMode(self.__forced_flags)
			except AttributeError:
				pass
			return True

	@staticmethod
	def shortest_line_data(p1, p2, p3, p4):

		p13 = Math.Vector3(p1.x - p3.x, p1.y - p3.y, p1.z - p3.z)
		p43 = Math.Vector3(p4.x - p3.x, p4.y - p3.y, p4.z - p3.z)

		if abs(p43.x) < EPSILONE and abs(p43.y) < EPSILONE and abs(p43.z) < EPSILONE:
			print ('Could not compute LineLineIntersect!')
			return None

		p21 = Math.Vector3(p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)

		if abs(p21.x) < EPSILONE and abs(p21.y) < EPSILONE and abs(p21.z) < EPSILONE:
			print ('Could not compute LineLineIntersect!')
			return None

		d1343 = p13.dot(p43)
		d4321 = p43.dot(p21)
		d1321 = p13.dot(p21)
		d4343 = p43.dot(p43)
		d2121 = p21.dot(p21)

		denom = d2121 * d4343 - d4321 * d4321

		if abs(denom) < EPSILONE:
			print ('Could not compute LineLineIntersect!')
			return None

		numer = d1343 * d4321 - d1321 * d4343

		mua = numer / denom
		mub = (d1343 + d4321 * mua) / d4343

		p1 = Math.Vector3(
			p1.x + mua * p21.x,
			p1.y + mua * p21.y,
			p1.z + mua * p21.z
		)
		p2 = Math.Vector3(
			p3.x + mub * p43.x,
			p3.y + mub * p43.y,
			p3.z + mub * p43.z
		)
		return p1, p2, (p1 - p2).length


class InteractiveMarker:

	def __init__(self, model, markerID, flash):
		self._model = model
		self._markerID = markerID
		self._flash = flash

	@property
	def model(self):
		return self._model

	@property
	def markerID(self):
		return self._markerID

	def update(self, cameraPosition, viewProjectionMatrix, screenWidth, screenHeight):
		if not self._flash:
			return
		position = Math.Vector3(self._model.position)
		posInClip = Math.Vector4(position.x, position.y, position.z, 1)
		posInClip = viewProjectionMatrix.applyV4Point(posInClip)
		if posInClip.w != 0.0:
			posInClip = posInClip.scale(1 / posInClip.w)

		self._flash.update({
			'position': [screenWidth * (posInClip.x + 1.0) / 2.0, screenHeight * (-posInClip.y + 1.0) / 2.0],
			'onScreen': posInClip.w != 0 and -1.1 <= posInClip.x / posInClip.w <= 1.1 and -1.1 <= posInClip.y / posInClip.w <= 1.1 and posInClip.z < 1,
			'deph': int((position - cameraPosition).length),
		})

class EditorController:

	def __init__(self):
		self.markers = {}
		self.flash = None
		self.interactive = None

	def onBattleLoaded(self):

		if not IS_EDITOR:
			return

		app = ServicesLocator.appLoader.getDefBattleApp()
		if app:
			app.loadView(SFViewLoadParams('BannersIntegrationInjector'))

	def onBattleClosed(self):

		if self.flash:
			self.flash.as_stopTimerS()
			self.flash.destroy()
		self.flash = None

		if self.interactive:
			self.interactive.destroy()
		self.interactive = None

		self.markers = {}

	def onModelAdded(self, model):
		if not self.flash:
			return
		markerID = str(uuid.uuid4())
		flash = self.flash.as_createMarkerS(markerID)
		self.markers[markerID] = InteractiveMarker(model, markerID, flash)

	def flashReady(self, flash):
		self.flash = flash
		for model in g_instance.models:
			self.onModelAdded(model)
		self.flash.as_startTimerS()

	def handleTimerPython(self):

		if not self.flash:
			return

		player = BigWorld.player()
		if not player:
			return

		camera = BigWorld.camera()
		viewProjectionMatrix = cameras.getViewProjectionMatrix()
		screenWidth = BigWorld.screenWidth()
		screenHeight = BigWorld.screenHeight()
		for marker in self.markers.values():
			marker.update(camera.position, viewProjectionMatrix, screenWidth, screenHeight)

		self.flash.as_updateDephS()

		debug_text = 'X: {:.2f} Y: {:.2f} Z: {:.2f} \nYAW: {:.2f} PITCH: {:.2f} ROLL: {:.2f}'.format(
			camera.position.x,
			camera.position.y,
			camera.position.z,
			camera.direction.x,
			camera.direction.y,
			camera.direction.z
		)
		self.flash.as_setDebugS(debug_text)

	def handleKeyEvent(self, event):
		
		# handle interactive
		if self.interactive:
			if event.key == Keys.KEY_ESCAPE:
				if not event.isKeyDown():
					self.interactive.destroy()
					self.interactive = None
					self.flash.as_markersVisibilityS(True)
				return True
			return self.interactive.handleKeyEvent(event)

		# hadle free cam
		if event.key == Keys.KEY_F1 and event.isCtrlDown():
			if event.isKeyDown():
				self.activate_free_cam()
			return True

		# hadle add model
		if event.key in MODEL_HOTKEYS.keys() and event.isCtrlDown():
			if event.isKeyDown():
				self.model_add(MODEL_HOTKEYS[event.key])
			return True

	def model_edit(self, marker_id):
		marker = self.markers[marker_id]
		if self.interactive:
			if self.interactive._model == marker.model:
				self.interactive.destroy()
				self.interactive = None
				return True
			self.interactive.destroy()
		self.interactive = InteractiveEditor(model=marker.model)
		self.flash.as_markersVisibilityS(False)

	def model_delete(self, marker_id):
		if marker_id not in self.markers:
			return
		self.flash.as_destroyMarkerS(marker_id)
		marker = self.markers[marker_id]
		del self.markers[marker_id]
		g_instance.models.remove(marker.model)
		for idx, (file_name, _) in enumerate(g_instance.entities):
			if file_name == marker.model.file_name:
				g_instance.entities.pop(idx)
		os.remove('%s/%s' % (DATA_PATH, marker.model.file_name))
		marker.model.destroy()
		del marker

	def model_add(self, model):
		model_path = MODEL_NAME_MASK % model
		if not vfs_file_exist(model_path):
			return False
		geometry = BigWorld.player().arena.arenaType.geometryName
		file_name = '%s_%d.json' % (geometry, time.time())
		cam = BigWorld.camera().position
		data = {
			'_version': DATA_VERSION,
			'model': model,
			'geometry': geometry,
			'position': [cam.x, cam.y, cam.z],
			'rotation': [0.0, 0.0, 0.0]
		}

		g_instance.entities.append((file_name, data))

		model = Model()
		if model.init(file_name, data):
			g_instance.models.append(model)
			model.dump()
			self.onModelAdded(model)

	def activate_free_cam(self):

		inputHandler = getattr(BigWorld.player(), 'inputHandler', None)
		if not inputHandler:
			return

		from BattleReplay import g_replayCtrl

		if g_replayCtrl.isControllingCamera:
			g_replayCtrl.appLoader.detachCursor(APP_NAME_SPACE.SF_BATTLE)
			g_replayCtrl._BattleReplay__replayCtrl.isControllingCamera = False
			g_replayCtrl.onControlModeChanged(CTRL_MODE_NAME.ARCADE)
			return BigWorld.callback(.0, self.activate_free_cam)

		if inputHandler.ctrlModeName == CTRL_MODE_NAME.ARCADE:
			inputHandler.onControlModeChanged(CTRL_MODE_NAME.VIDEO, prevModeName=inputHandler.ctrlModeName,
									 camMatrix=BigWorld.camera().matrix)
			if inputHandler.ctrlModeName == CTRL_MODE_NAME.ARCADE:
				g_replayCtrl._BattleReplay__timeWarp(g_replayCtrl.currentTime + 1)
				return BigWorld.callback(.0, self.activate_free_cam)

		if inputHandler.ctrlModeName == CTRL_MODE_NAME.VIDEO:
			inputHandler.ctrl.camera._inertiaEnabled = True
			inputHandler.ctrl.camera._movementSensor.sensitivity = 10

editor_ctrl = EditorController()

class BannersIntegrationUI(BaseDAAPIComponent):

	def _populate(self):
		super(BannersIntegrationUI, self)._populate()
		editor_ctrl.flashReady(self)

	def as_setDebugS(self, data):
		if self._isDAAPIInited():
			return self.flashObject.as_setDebug(data)

	def as_updateDephS(self):
		if self._isDAAPIInited():
			return self.flashObject.as_updateDeph()

	def as_startTimerS(self):
		if self._isDAAPIInited():
			return self.flashObject.as_startTimer()

	def as_stopTimerS(self):
		if self._isDAAPIInited():
			return self.flashObject.as_stopTimer()

	def as_destroyMarkerS(self, markerID):
		if self._isDAAPIInited():
			self.flashObject.as_destroyMarker(markerID)

	def as_createMarkerS(self, type):
		if self._isDAAPIInited():
			return self.flashObject.as_createMarker(type)

	def as_refreshDepthS(self):
		if self._isDAAPIInited():
			self.flashObject.as_refreshDepth()

	def as_markersVisibilityS(self, isVisible):
		if self._isDAAPIInited():
			self.flashObject.as_markersVisibility(isVisible)

	def handleTimerPython(self):
		editor_ctrl.handleTimerPython()

	def clickEdit(self, markerID):
		editor_ctrl.model_edit(markerID)

	def clickDelete(self, markerID):
		editor_ctrl.model_delete(markerID)

	def destroy(self):
		if self.getState() != EntityState.CREATED:
			return
		super(BannersIntegrationUI, self).destroy()

g_entitiesFactories.addSettings(
	ViewSettings('BannersIntegrationInjector', View, 'bannersIntegration.swf', WindowLayer.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE)
)

g_entitiesFactories.addSettings(
	ViewSettings('BannersIntegrationOverlay', BannersIntegrationUI, None, WindowLayer.UNDEFINED, None, ScopeTemplates.DEFAULT_SCOPE)
)

battle_state.onBattleLoaded += editor_ctrl.onBattleLoaded
battle_state.onBattleClosed += editor_ctrl.onBattleClosed
