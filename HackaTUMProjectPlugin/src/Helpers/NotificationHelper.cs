using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.Versioning;

namespace Loupedeck.HackaTUMProjectPlugin.Helpers;

[SupportedOSPlatform("windows")]
public static class NotificationHelper
{
    public static void SendSystemNotification(string title, string message)
    {
        try 
        {
            LogToFile($"Bereite PowerShell Toast vor: {title}");

            // Wir bauen ein PowerShell-Skript, das zur Laufzeit ausgeführt wird.
            // Es lädt WinForms NUR für diesen kurzen Moment im PowerShell-Prozess.
            string psCommand = $@"
                Add-Type -AssemblyName System.Windows.Forms;
                $icon = New-Object System.Windows.Forms.NotifyIcon;
                $icon.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon((Get-Process -Id $pid).Path);
                $icon.BalloonTipIcon = 'Info';
                $icon.BalloonTipText = '{message}';
                $icon.BalloonTipTitle = '{title}';
                $icon.Visible = $true;
                $icon.ShowBalloonTip(5000);
                Start-Sleep -Seconds 5;
                $icon.Dispose();
            ";

            // Prozess-Starter konfigurieren
            var psi = new ProcessStartInfo()
            {
                FileName = "powershell.exe",
                Arguments = $"-NoProfile -ExecutionPolicy Bypass -Command \"{psCommand}\"",
                UseShellExecute = false,
                CreateNoWindow = true, // Wichtig: Kein schwarzes Fenster anzeigen!
                WindowStyle = ProcessWindowStyle.Hidden
            };

            // Feuer frei!
            Process.Start(psi);
            
            LogToFile("PowerShell Befehl abgesendet.");
        }
        catch (Exception ex)
        {
            LogToFile($"CRASH (PowerShell): {ex.Message}");
        }
    }

    private static void LogToFile(string text)
    {
        try {
            var desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
            var filePath = Path.Combine(desktopPath, "HackaTUM_Log.txt");
            File.AppendAllText(filePath, $"{DateTime.Now}: {text}\n");
        } catch {}
    }
}