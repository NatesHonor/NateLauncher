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
                    LaunchElevatedLauncher("missionchief", path);
                }
                return null;
            }
        }

        public static async Task<bool> CheckAndRunInstaller(string installPath, string program)
        {
            try
            {
                if (!Directory.Exists(installPath))
                {
                    Directory.CreateDirectory(installPath);
                }

                string tempFilePath = Path.Combine(installPath, "temp.txt");
                File.WriteAllText(tempFilePath, "test");
                File.Delete(tempFilePath);

                Debug.WriteLine("Successfully wrote to the directory. Using non-elevated installer.");
                await Installer.InstallProgram(program, installPath);
                Debug.WriteLine("Non-elevated installer finished.");
                return true;
            }
            catch (UnauthorizedAccessException)
            {
                Debug.WriteLine("Failed to write to the directory. Launching elevated installer.");
                MessageBox.Show("The installation directory requires elevated permissions. The installer will now run with elevated permissions.", "Permission Required", MessageBoxButton.OK, MessageBoxImage.Warning);
                LaunchElevatedLauncher(program, installPath);
                return false;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error: {ex.Message}. Launching elevated installer.");
                MessageBox.Show($"An error occurred: {ex.Message}. The installer will now run with elevated permissions.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                LaunchElevatedLauncher(program, installPath);
                return false;
            }
        }

        public static void LaunchElevatedLauncher(string program, params string[] args)
        {
            var escapedArgs = string.Join(" ", args.Select(arg => $"\"{arg}\""));

            var processInfo = new ProcessStartInfo
            {
                FileName = @"C:\Program Files (x86)\Nate Launcher\NateLauncherElevated.exe",
                Arguments = $"{program} {escapedArgs}",
                UseShellExecute = true,
                Verb = "runas"
            };

            try
            {
                Process.Start(processInfo);
                Debug.WriteLine($"Successfully launched elevated installer with program: {program} and arguments: {escapedArgs}");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred while trying to launch the elevated installer: {ex.Message}");
                Debug.WriteLine($"Error launching elevated installer: {ex.Message}");
            }
        }
    }
}
