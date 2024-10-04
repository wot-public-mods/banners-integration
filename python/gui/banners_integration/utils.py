# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2024 Andrii Andrushchyshyn

import types

import BigWorld
import Keys
import Math
import ResMgr

__all__ = ('byteify', 'override', 'checkKeySet', 'vfs_file_exist', 'pack_vector')

def override(holder, name, wrapper=None, setter=None):
	"""Override methods, properties, functions, attributes
	:param holder: holder in which target will be overrided
	:param name: name of target to be overriden
	:param wrapper: replacement for override target
	:param setter: replacement for target property setter"""
	if wrapper is None:
		return lambda wrapper, setter=None: override(holder, name, wrapper, setter)
	target = getattr(holder, name)
	wrapped = lambda *a, **kw: wrapper(target, *a, **kw)
	if not isinstance(holder, types.ModuleType) and isinstance(target, types.FunctionType):
		setattr(holder, name, staticmethod(wrapped))
	elif isinstance(target, property):
		prop_getter = lambda *a, **kw: wrapper(target.fget, *a, **kw)
		prop_setter = target.fset if not setter else lambda *a, **kw: setter(target.fset, *a, **kw)
		setattr(holder, name, property(prop_getter, prop_setter, target.fdel))
	else:
		setattr(holder, name, wrapped)

def byteify(data):
	"""Encodes data with UTF-8
	:param data: Data to encode"""
	result = data
	if isinstance(data, dict):
		result = {byteify(key): byteify(value) for key, value in data.iteritems()}
	elif isinstance(data, (list, tuple, set)):
		result = [byteify(element) for element in data]
	elif isinstance(data, unicode):
		result = data.encode('utf-8')
	return result

VKEY_ALT, VKEY_CONTROL, VKEY_SHIFT = range(-1, -4, -1)
VKEYS_MAP = {
	VKEY_ALT: (Keys.KEY_LALT, Keys.KEY_RALT),
	VKEY_CONTROL: (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL),
	VKEY_SHIFT: (Keys.KEY_LSHIFT, Keys.KEY_RSHIFT),
}
def checkKeySet(data, keyCode=None):
	"""Verify is keys is pressed
	:param data: list of keys to be checked
	:param keyCode: pressed keyCode"""
	result, fromSet = True, False
	if not data:
		result = False
	for key in data:
		if isinstance(key, int):
			# virtual special keys
			if key in (VKEY_ALT, VKEY_CONTROL, VKEY_SHIFT):
				result &= any(map(BigWorld.isKeyDown, VKEYS_MAP[key]))
				fromSet |= keyCode in VKEYS_MAP[key]
			# BW Keys
			elif not BigWorld.isKeyDown(key):
				result = False
				fromSet |= keyCode == key
		# old special keys
		if isinstance(key, list):
			result &= any(map(BigWorld.isKeyDown, key))
			fromSet |= keyCode in key
	if keyCode is not None:
		return result, fromSet
	return result

def vfs_file_exist(path):
	file = ResMgr.openSection(path)
	return file is not None and ResMgr.isFile(path)

def pack_vector(vector, precision=3):
	result = [round(vector.x, precision), round(vector.y, precision)]
	if isinstance(vector, Math.Vector3):
		result.append(round(vector.z, precision))
	if isinstance(vector, Math.Vector4):
		result.append(round(vector.w, precision))
	return result
