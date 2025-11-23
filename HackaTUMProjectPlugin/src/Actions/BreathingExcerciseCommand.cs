namespace Loupedeck.HackaTUMProjectPlugin.Actions
{
    using System;
    using System.Runtime.Versioning;

    using Helpers;

    // This class implements an example command that counts button presses.

    [SupportedOSPlatform("windows10.0.17763.0")]
    public class BreathingExcerciseCommand() : PluginDynamicCommand(displayName: "Breathing Excercise",
        description: "Guides you through a calming breathing excercise", groupName: "Commands")
    {
        
        private bool _active = false;

        // This method is called when the user executes the command.
        protected override void RunCommand(String actionParameter)
        {
            if (!this._active)
            {
                this._active = true;
                NotificationHelper.SendSystemNotification("MX Master 4",
                    "Pick up the mouse and hold it between your hands. Breathe in and out on the vibration cues. (Start in 5s)");
                Thread.Sleep(5000);

                for (var i = 0; i < 5; i++)
                {
                    this.Plugin.PluginEvents.RaiseEvent("breathe_state_change1");
                    Thread.Sleep(1000);

                    for (var j = 0; j < 4; j++)
                    {
                        this.Plugin.PluginEvents.RaiseEvent("breathe_state_change2");
                        Thread.Sleep(1000);
                    }

                    this.Plugin.PluginEvents.RaiseEvent("breathe_state_change1");

                    for (var j = 0; j < 4; j++)
                    {
                        this.Plugin.PluginEvents.RaiseEvent("breathe_state_change2");
                        Thread.Sleep(1000);
                    }
                }

                this.Plugin.PluginEvents.RaiseEvent("completed");
                NotificationHelper.SendSystemNotification("MX Master 4",
                    "Congratulations on completing your breathing excercise :)");
                this._active = false;
            }
        }

        // This method is called when Loupedeck needs to show the command on the console or the UI.
        protected override String GetCommandDisplayName(String actionParameter, PluginImageSize imageSize) =>
            "Breathwork";
    }
}
