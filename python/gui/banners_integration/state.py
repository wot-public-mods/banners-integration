# SPDX-License-Identifier: MIT
# Copyright (c) 2017-2024 Andrii Andrushchyshyn

class BattleStateEvents(object):

	# prop alternateState -> bool
	# prop colorBlind -> bool

	# event onBattleLoaded()
	# event onBattleClosed()
	# event onGUIVisibility(bool)
	# event onAlternateState(bool)
	# event onColorBlind(bool)

	@property
	def visible(self):
		return not any((
			self._hiddenByInterface, 
			self._hiddenByStatsPopup, 
			self._hiddenByKillCam 
		))

	@property
	def alternateState(self):
		return self._alternateState

	@property
	def colorBlind(self):
		return self._colorBlind

	def __init__(self):
		import Event
		from gui.shared import g_eventBus, EVENT_BUS_SCOPE
		from gui.shared.events import GameEvent
		from gui.shared.personality import ServicesLocator

		self._hiddenByInterface = False
		self._hiddenByStatsPopup = False
		self._hiddenByKillCam = False

		self._alternateState = False
		self._colorBlind = False

		self.onBattleLoaded = Event.SafeEvent()
		self.onBattleClosed = Event.SafeEvent()
		self.onGUIVisibility = Event.SafeEvent()
		self.onAlternateState = Event.SafeEvent()
		self.onColorBlind = Event.SafeEvent()

		ServicesLocator.appLoader.onGUISpaceEntered += self._onGUISpaceEntered
		ServicesLocator.appLoader.onGUISpaceLeft += self._onGUISpaceLeft
		ServicesLocator.settingsCore.onSettingsChanged += self._onSettingsChanged

		g_eventBus.addListener(GameEvent.GUI_VISIBILITY, self._onGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
		g_eventBus.addListener(GameEvent.FULL_STATS, self._onToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
		g_eventBus.addListener(GameEvent.FULL_STATS_QUEST_PROGRESS, self._onToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
		g_eventBus.addListener(GameEvent.FULL_STATS_PERSONAL_RESERVES, self._onToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
		g_eventBus.addListener(GameEvent.EVENT_STATS, self._onToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
		g_eventBus.addListener(GameEvent.SHOW_EXTENDED_INFO, self._handleShowExtendedInfo, scope=EVENT_BUS_SCOPE.BATTLE)

	def _onSettingsChanged(self, diff, isForced=False):
		from account_helpers.settings_core.settings_constants import GRAPHICS
		if GRAPHICS.COLOR_BLIND in diff:
			self._colorBlind = diff[GRAPHICS.COLOR_BLIND]
			self.onColorBlind(self._colorBlind)

	def _onGUISpaceEntered(self, spaceID):
		from skeletons.gui.app_loader import GuiGlobalSpaceID
		if spaceID == GuiGlobalSpaceID.BATTLE:
			self._hiddenByInterface = False
			self._hiddenByStatsPopup = False
			self._handleBattleLoad()
			self.onBattleLoaded()

	def _onGUISpaceLeft(self, spaceID):
		from skeletons.gui.app_loader import GuiGlobalSpaceID
		if spaceID == GuiGlobalSpaceID.BATTLE:
			self.onBattleClosed()

	def _onGUIVisibility(self, event):
		hidden = not event.ctx['visible']
		if hidden != self._hiddenByInterface:
			self._hiddenByInterface = hidden
			self.onGUIVisibility(self.visible)

	def _onToggleFullStats(self, event):
		hidden = event.ctx['isDown']
		if hidden != self._hiddenByStatsPopup:
			self._hiddenByStatsPopup = hidden
			self.onGUIVisibility(self.visible)

	def _handleShowExtendedInfo(self, event):
		state = event.ctx['isDown']
		if state != self._alternateState:
			self._alternateState = state
			self.onAlternateState(self._alternateState)

	def _handleBattleLoad(self):
		from account_helpers.settings_core.settings_constants import GRAPHICS
		from helpers import dependency
		from skeletons.account_helpers.settings_core import ISettingsCore
		from skeletons.gui.battle_session import IBattleSessionProvider

		sessionProvider = dependency.instance(IBattleSessionProvider)
		settingsCore = dependency.instance(ISettingsCore)

		# reset colorblind state
		self._colorBlind = settingsCore.getSetting(GRAPHICS.COLOR_BLIND)

		# reset alternate state
		self._alternateState = False

		# reset hidden flags
		self._hiddenByInterface = False
		self._hiddenByStatsPopup = False
		self._hiddenByKillCam = False

		# subscribe to kill cam
		killCamCtrl = getattr(sessionProvider.shared, 'killCamCtrl', None)
		if killCamCtrl:
			killCamCtrl.onKillCamModeStateChanged += self.__onKillCamStateChanged

	def __onKillCamStateChanged(self, state, *a, **kw):
		from gui.shared.events import DeathCamEvent
		_s = DeathCamEvent.State
		hidden = _s.STARTING.value <= state.value < _s.FINISHED.value
		if self._hiddenByKillCam != hidden:
			self._hiddenByKillCam = hidden
		self.onGUIVisibility(self.visible)

battle_state = BattleStateEvents()
