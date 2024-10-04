package mods.common
{
	import flash.events.Event;

	import net.wg.gui.battle.views.BaseBattlePage;
	import net.wg.gui.battle.components.BattleUIDisplayable;
	
	public class BattleDisplayable extends BattleUIDisplayable
	{
		public var battlePage:BaseBattlePage;
		public var componentName:String;

		public function initBattle() : void 
		{
			if (!battlePage.contains(this)) 
				battlePage.addChild(this);
			if (!battlePage.isFlashComponentRegisteredS(componentName)) 
				battlePage.registerFlashComponentS(this, componentName);
		}

		public function finiBattle() : void 
		{
			if (battlePage.isFlashComponentRegisteredS(componentName)) 
				battlePage.unregisterFlashComponentS(componentName);
			if (battlePage.contains(this)) 
				battlePage.removeChild(this);
		}

		override protected function onPopulate() : void 
		{
			super.onPopulate();
			battlePage.addEventListener(Event.RESIZE, _handleResize);
		}
		
		override protected function onDispose() : void 
		{
			battlePage.removeEventListener(Event.RESIZE, _handleResize);
			finiBattle();
			super.onDispose();
		}
		
		private function _handleResize(e:Event) : void
		{
			onResized();
		}

		protected function onResized() : void
		{

		}
	}
}