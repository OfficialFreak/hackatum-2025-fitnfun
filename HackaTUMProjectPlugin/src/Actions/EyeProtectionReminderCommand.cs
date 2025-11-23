namespace Loupedeck.HackaTUMProjectPlugin.Actions
{
    using System;
    using System.Runtime.Versioning;

    using Helpers;

    // This class implements an example command that counts button presses.

    [SupportedOSPlatform("windows10.0.17763.0")]
    public class EyeProtectionReminderCommand() : PluginDynamicCommand(displayName: "Eye Protection Reminders",
        description: "Gives you gentle reminders to look away from your screen every 20 minutes", groupName: "Commands")
    {
        
        private bool _active = false;
        private bool _running_instance = false;

        // This method is called when the user executes the command.
        protected override void RunCommand(String actionParameter)
        {
            if (!this._active)
            {
                this._active = true;
                NotificationHelper.SendSystemNotification("MX Master 4", "Your mouse will remind you with this vibration pattern and vibrate again after 20 seconds");
                this.Plugin.PluginEvents.RaiseEvent("eye_protection_reminder");
                Thread.Sleep(1000);
                this.Plugin.PluginEvents.RaiseEvent("eye_protection_reminder");
            
                // Change text
                this.ActionImageChanged(actionParameter);

                if (!this._running_instance)
                {
                    this._running_instance = true;
                    while (this._active)
                    {
                        Thread.Sleep(1000 * 60 * 1);
                        this.Plugin.PluginEvents.RaiseEvent("eye_protection_reminder");
                        Thread.Sleep(1000);
                        this.Plugin.PluginEvents.RaiseEvent("eye_protection_reminder");
                        Thread.Sleep(1000 * 20);
                        this.Plugin.PluginEvents.RaiseEvent("eye_protection_reminder");
                    }   
                    this._running_instance = false;
                }
            }
            else
            {
                this._active = false;
                this.ActionImageChanged(actionParameter);
            }
        }

        // This method is called when Loupedeck needs to show the command on the console or the UI.
        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) =>
            this._active ? "Disable Vision Guard" : "Vision Guard";
    }
}