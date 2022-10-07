
import BigWorld
import game
import Keys

from helpers import isPlayerAvatar
from gui.shared.personality import ServicesLocator
from skeletons.gui.app_loader import GuiGlobalSpaceID

from .controller import g_instance, keysMapping, Model
from ._constants import IS_DEV
from .utils import checkKeySet, override

__all__ = ()

@override(game, 'handleKeyEvent')
def handleKeyEvent(baseMethod, event):
	if not IS_DEV or not isPlayerAvatar() or (not event.isKeyDown() and not event.isKeyUp()):
		return baseMethod(event)
	if not checkKeySet([Keys.KEY_LCONTROL]):
		return baseMethod(event)
	for keySet, action in keysMapping:
		if checkKeySet(keySet):
			return action()
	return False

def onGUISpaceEntered(spaceID):
	if spaceID != GuiGlobalSpaceID.BATTLE:
		return
	g_instance.cleanup()
	geometryName = BigWorld.player().arena.arenaType.geometryName
	for name, data in g_instance.modelsRaw:
		if data['geometryName'] != str(geometryName):
			continue
		model = Model()
		result = model.setData(name, data)
		if result:
			g_instance.models.append(model)
ServicesLocator.appLoader.onGUISpaceEntered += onGUISpaceEntered

def onGUISpaceLeft(spaceID):
	if spaceID != GuiGlobalSpaceID.BATTLE:
		return
	g_instance.cleanup()
ServicesLocator.appLoader.onGUISpaceLeft += onGUISpaceLeft
