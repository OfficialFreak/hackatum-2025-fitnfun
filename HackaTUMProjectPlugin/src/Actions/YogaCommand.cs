namespace Loupedeck.HackaTUMProjectPlugin.Actions
{
    using System;
    using System.Runtime.Versioning;

    using Helpers;

    [SupportedOSPlatform("windows10.0.17763.0")]
    public class YogaCommand() : PluginDynamicCommand(displayName: "Yoga Training",
        description: "Guides you through a refreshing yoga session", groupName: "Commands")
    {
        
        private bool _active = false;
        
        // This method is called when the user executes the command.
        protected override void RunCommand(String actionParameter)
        {
            if (!this._active)
            {
                this._active = true;
                NotificationHelper.SendSystemNotification("MX Master 4", "Pick up the mouse and hold it between your hands.");
                Thread.Sleep(1000);
                NotificationHelper.SendSystemNotification("Seated Twist", "Sit back in your chair. As you inhale, lift your arms over your head and as you exhale, twist to your right, placing both hands on the right armrest for support.");
                Thread.Sleep(60000);
                this.Plugin.PluginEvents.RaiseEvent("completed");
            
                NotificationHelper.SendSystemNotification("Seated Twist", "Now, lift your arms over your head and as you exhale, twist to your left, placing both hands on the left armrest for support.");
                Thread.Sleep(60000);
                this.Plugin.PluginEvents.RaiseEvent("completed");
            
                NotificationHelper.SendSystemNotification("Shoulder Rolls", "As you inhale, draw your shoulders up toward your ears and bring them back down. Then, on the exhale, move them down and forward. Repeat this motion two more times in the same direction, then reverse it.");
                Thread.Sleep(20000);
                this.Plugin.PluginEvents.RaiseEvent("completed");
            
                NotificationHelper.SendSystemNotification("Seated Crescent Moon Pose", "Sitting in your desk chair, lift your arms over your head, and place your palms together. Lean to the right, and hold this pose for 15 seconds.");
                Thread.Sleep(15000);
                this.Plugin.PluginEvents.RaiseEvent("completed");
            
                NotificationHelper.SendSystemNotification("Seated Crescent Moon Pose", "Repeat for the left side now.");
                Thread.Sleep(15000);
                this.Plugin.PluginEvents.RaiseEvent("completed");
            
                NotificationHelper.SendSystemNotification("MX Master 4", "Congratulations on completing your quick yoga session :)");
                this._active = false;
            }
        }

        // This method is called when Loupedeck needs to show the command on the console or the UI.
        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) =>
            "Yoga Training";
    }   
}