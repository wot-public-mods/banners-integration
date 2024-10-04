# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2024 Andrii Andrushchyshyn

import BattleReplay
import game

from helpers import isPlayerAvatar

from ._constants import IS_EDITOR
from .editor import editor_ctrl
from .utils import override

@override(game, 'handleKeyEvent')
def handleKeyEvent(baseMethod, event):

	if not IS_EDITOR:
		return baseMethod(event)

	if not BattleReplay.isPlaying():
		return baseMethod(event)

	if not isPlayerAvatar():
		return baseMethod(event)

	if editor_ctrl.handleKeyEvent(event):
		return True

	return baseMethod(event)
