package me.poliroid.battle.bannersintegration
{
	import flash.display.Sprite;
	import scaleform.clik.events.ButtonEvent;
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.infrastructure.base.UIComponentEx;

	public class InteractiveMarker extends UIComponentEx
	{

		public var markerID:String;
		public var deph:Number;
		public var highlightMC:Sprite;
		public var editButton:SoundButtonEx;
		public var deleteButton:SoundButtonEx;

		override protected function configUI() : void
		{
			super.configUI();
			focusable = true;
			editButton.addEventListener(ButtonEvent.PRESS, _handleClickEdit);
			deleteButton.addEventListener(ButtonEvent.PRESS, _handleClickDelete);
		}

		public function update(context:Object): void
		{
			deph = context.deph;
			visible = context.onScreen;
			if (!visible)
				return;
			x = context.position[0];
			y = context.position[1];
			editButton.alpha = deleteButton.alpha = deph > 100 ? 0.0 : 1.1 - deph / 100.0;
			highlightMC.alpha = deph > 100 ? 1.0 : deph / 100.0;
		}

		public function _handleClickEdit(e:ButtonEvent) : void 
		{
			((parent as Sprite).parent as MarkersManagerEx).clickEdit(markerID);
		}

		public function _handleClickDelete(e:ButtonEvent) : void 
		{
			((parent as Sprite).parent as MarkersManagerEx).clickDelete(markerID);
		}
	}
}