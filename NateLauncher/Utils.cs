using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;

namespace NateLauncher
{
    public static class Utils
    {
        public static string ReadFileWithAdminCheck(string path)
        {
            try
            {
                return File.ReadAllText(path);
            }
            catch (UnauthorizedAccessException)
            {
                if (MessageBox.Show("Nate Launcher requires elevated permission to read this file. Would you like to continue?", "Permission Required", MessageBoxButton.YesNo, MessageBoxImage.Question) == MessageBoxResult.Yes)
                {
                    LaunchElevatedLauncher("InstallProgram", "missionchief", path);
                }
                return null;
            }
        }

        public static async Task CheckAndRunInstaller(string installPath, string program)
        {
            if (ReadFileWithAdminCheck(installPath) == null)
            {
                MessageBox.Show("Install Location Requires Elevated Permission", "Permission Required", MessageBoxButton.OK, MessageBoxImage.Warning);
                LaunchElevatedLauncher("InstallProgram", "missionchief", installPath);
                return;
            }

            try
            {
                if (!Directory.Exists(installPath))
                {
                    Directory.CreateDirectory(installPath);
                }

                string tempFilePath = Path.Combine(installPath, "temp.txt");
                File.WriteAllText(tempFilePath, "test");
                File.Delete(tempFilePath);
                Debug.WriteLine("Administrator check passed.");
                Debug.WriteLine("Running non-elevated installer.");
                await Installer.InstallProgram(program, installPath);
                Debug.WriteLine("Non-elevated installer finished.");
            }
            catch (UnauthorizedAccessException)
            {
                Debug.WriteLine("Administrator check failed. Launching elevated installer.");
                LaunchElevatedLauncher("InstallProgram", "missionchief", installPath);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error: {ex.Message}. Launching elevated installer.");
                LaunchElevatedLauncher("InstallProgram", "missionchief", installPath);
            }
        }

        public static void LaunchElevatedLauncher(string action, params string[] args)
        {
            var escapedArgs = string.Join(" ", args.Select(arg => $"\"{arg}\""));

            var processInfo = new ProcessStartInfo
            {
                FileName = @"C:\Program Files (x86)\Nate Launcher\NateLauncherElevated.exe",
                Arguments = $"{action} {escapedArgs}",
                UseShellExecute = true,
                Verb = "runas"
            };

            try
            {
                Process.Start(processInfo);
                Debug.WriteLine($"Successfully launched elevated installer with action: {action} and arguments: {escapedArgs}");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred while trying to launch the elevated installer: {ex.Message}");
                Debug.WriteLine($"Error launching elevated installer: {ex.Message}");
            }
        }
    }
}
