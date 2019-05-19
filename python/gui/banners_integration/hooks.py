
import BigWorld
import game
import Keys

from gui.shared.personality import ServicesLocator
from helpers import isPlayerAvatar
from skeletons.gui.app_loader import GuiGlobalSpaceID

from gui.banners_integration.controller import g_instance, keysMapping, Model
from gui.banners_integration._constants import IS_DEV
from gui.banners_integration.utils import checkKeySet, override

__all__ = ()

@override(game, 'handleKeyEvent')
def handleKeyEvent(baseMethod, event):
	if not IS_DEV:
		return baseMethod(event)
	if not isPlayerAvatar():
		return baseMethod(event)
	if not event.isKeyDown() and not event.isKeyUp():
		return baseMethod(event)
	for (keySet, action, ) in keysMapping:
		if checkKeySet(keySet):
			return action()
	if not checkKeySet([Keys.KEY_LCONTROL]):
		return baseMethod(event)
	return False

def onGUISpaceEntered(spaceID):
	if spaceID != GuiGlobalSpaceID.BATTLE:
		return
	g_instance.clean()
	geometryName = BigWorld.player().arena.arenaType.geometryName
	for (name, data) in g_instance.modelsRaw:
		if data['geometryName'] != str(geometryName):
			continue
		model = Model()
		model.setData(name, data)
		g_instance.models.append(model)
ServicesLocator.appLoader.onGUISpaceEntered += onGUISpaceEntered

def onGUISpaceLeft(spaceID):
	if spaceID != GuiGlobalSpaceID.BATTLE:
		return
	g_instance.clean()
ServicesLocator.appLoader.onGUISpaceLeft += onGUISpaceLeft
