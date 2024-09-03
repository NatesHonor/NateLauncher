using Newtonsoft.Json;
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
        private static readonly string LogFilePath = @"C:\Program Files (x86)\Nate Launcher\Utils.log";

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
                    LaunchElevatedLauncher("ReadFile", path);
                }
                return null;
            }
        }

        public static void SavePathToJson(string path)
        {
            var config = new { Missionchief = path };
            string json = JsonConvert.SerializeObject(config, Formatting.Indented);
            LaunchElevatedLauncher("InstallProgram", "missionchief", path, json);
        }

        public static void LaunchElevatedInstaller()
        {
            LaunchElevatedLauncher("InstallProgram");
        }

        public static async Task CheckAndRunInstaller(string installPath, string program)
        {
            if (ReadFileWithAdminCheck(installPath) == null)
            {
                MessageBox.Show("Install Location Requires Elevated Permission", "Permission Required", MessageBoxButton.OK, MessageBoxImage.Warning);
                LaunchElevatedInstaller();
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
                Log("Administrator check passed.");
                Log("Running non-elevated installer.");
                await Installer.InstallProgram(program, installPath);
                Log("Non-elevated installer finished.");
            }
            catch (UnauthorizedAccessException)
            {
                Log("Administrator check failed. Launching elevated installer.");
                LaunchElevatedInstaller();
            }
            catch (Exception ex)
            {
                Log($"Error: {ex.Message}. Launching elevated installer.");
                LaunchElevatedInstaller();
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
                Log($"Successfully launched elevated installer with action: {action} and arguments: {escapedArgs}");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred while trying to launch the elevated installer: {ex.Message}");
                Log($"Error launching elevated installer: {ex.Message}");
            }
        }

        private static void Log(string message)
        {
            try
            {
                File.AppendAllText(LogFilePath, $"{DateTime.Now}: {message}\n");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Logging failed: {ex.Message}");
            }
        }
    }
}
