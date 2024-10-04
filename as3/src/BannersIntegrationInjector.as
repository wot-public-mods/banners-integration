package
{
	import mods.common.AbstractComponentInjector;
	
	public class BannersIntegrationInjector extends AbstractComponentInjector 
	{
		override protected function onPopulate() : void 
		{
			autoDestroy = false;
			componentName = 'BannersIntegrationOverlay';
			componentUI = BannersIntegration;
			super.onPopulate();
		}
	}
}