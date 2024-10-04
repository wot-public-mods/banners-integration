package me.poliroid.battle.bannersintegration
{

	import flash.text.TextField;
	import flash.display.MovieClip;
	import flash.display.DisplayObject;
	import flash.events.TimerEvent;
	import flash.utils.Timer;

	import mods.common.BattleDisplayable;

	public class MarkersManagerEx extends BattleDisplayable
	{
		private var markers:Vector.<InteractiveMarker> = new Vector.<InteractiveMarker>();
		private var _markers_sprite:MovieClip;

		public var clickEdit:Function = null;
		public var clickDelete:Function = null;

		private var frame_timer:Timer = null;
		public var handleTimerPython:Function = null;

		public var debugTF:TextField = null;

		public function MarkersManagerEx(): void
		{
			super();

			debugTF.mouseEnabled = false;
			debugTF.mouseWheelEnabled = false;

			_markers_sprite = new MovieClip();
			addChild(_markers_sprite);
		}

		public function as_setDebug(str): void
		{
			if (debugTF)
				debugTF.text = str;
		}

		public function as_startTimer() : void
		{
			as_stopTimer();
			frame_timer = new Timer(1);
			frame_timer.addEventListener(TimerEvent.TIMER, _handleTimer);
			frame_timer.start();
		}

		public function as_stopTimer() : void
		{
			if (frame_timer)
				frame_timer.stop();
			frame_timer = null;
		}

		public function as_createMarker(markerID:String): DisplayObject
		{
			var marker:InteractiveMarker = new InteractiveMarker();
			marker.markerID = markerID;
			markers.push(marker);
			_markers_sprite.addChild(marker);
			return marker as DisplayObject;
		}

		public function as_destroyMarker(markerID:String): Boolean
		{
			var marker:InteractiveMarker;
			for each (marker in markers)
				if (marker.markerID == markerID)
					break;
			if (marker == null)
				return false;
			markers.splice(markers.indexOf(marker), 1);
			if (marker.stage)
				marker.parent.removeChild(marker);
			marker = null;
			return true;
		}

		private function _handleTimer(): void
		{
			if (handleTimerPython == null)
				return;
			handleTimerPython();
		}

		public function as_markersVisibility(isVisible) : void
		{
			if (_markers_sprite == null)
				return;
			_markers_sprite.visible = isVisible;
		}

		public function as_updateDeph() : void
		{
			if (_markers_sprite == null)
				return;
			markers.sort(_sortDesc);
			for (var index:int = 0; index<markers.length; index++)
				_markers_sprite.setChildIndex(markers[index], index);
		}

		private function _sortDesc(a, b) : int
		{
			return a.deph < b.deph ? 1 : (a.deph > b.deph ? -1 : 0);
		}
	}
}
