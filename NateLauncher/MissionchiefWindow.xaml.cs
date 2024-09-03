using System;
using System.Diagnostics;
using System.IO;
using System.IO.Pipes;
using System.Security.Principal;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using Newtonsoft.Json;

namespace NateLauncher
{
    public partial class MissionchiefWindow : Window
    {
        public MissionchiefWindow()
        {
            InitializeComponent();
            CheckInstallStatus();
        }

        private async void InstallButton_Click(object sender, RoutedEventArgs e)
        {
            Log("Install button clicked.");
            string program = "missionchief";

            if (InstallButton.Content.ToString() == "Start")
            {
                MessageBox.Show("Starting the application...");
                return;
            }

            var dialog = new InstallPathDialog();
            dialog.PathTextBox.Text = @"C:\Nate Launcher";
            if (dialog.ShowDialog() == true)
            {
                string installPath = dialog.PathTextBox.Text;
                SavePathToJson(installPath);

                if (!IsAdministrator())
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
                        Log("Administrator check passed.");
                        Log("Running non-elevated installer.");
                        await Installer.InstallProgram(program, installPath);
                        Log("Non-elevated installer finished.");

                        InstallButton.Content = "Start";
                    }
                    catch (UnauthorizedAccessException)
                    {
                        Log("Administrator check failed. Launching elevated installer.");
                        LaunchElevatedInstaller(program, installPath);
                        return;
                    }
                }
            }
        }

        private bool IsAdministrator()
        {
            var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            bool isAdmin = principal.IsInRole(WindowsBuiltInRole.Administrator);
            Log($"IsAdministrator: {isAdmin}");
            return isAdmin;
        }

        private void LaunchElevatedInstaller(string program, string path)
        {
            var processInfo = new ProcessStartInfo
            {
                FileName = @"C:\Program Files (x86)\Nate launcher\NateLauncherElevated.exe",
                Arguments = $"\"{program}\" \"{path}\"",
                UseShellExecute = true,
                Verb = "runas"
            };

            try
            {
                Process.Start(processInfo);
                Log("Elevated installer launched.");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred while trying to launch the elevated installer: {ex.Message}");
                Log($"Error launching elevated installer: {ex.Message}");
            }
        }

        private void Log(string message)
        {
            Debug.WriteLine(message);
        }

        private void SavePathToJson(string path)
        {
            var config = new { Missionchief = path };
            string json = JsonConvert.SerializeObject(config, Formatting.Indented);
            File.WriteAllText(@"C:\Nate Launcher\Nate Launcher.json", json);
        }

        private void CheckInstallStatus()
        {
            string jsonFilePath = @"C:\Nate Launcher\Nate Launcher.json";
            if (File.Exists(jsonFilePath))
            {
                string json = File.ReadAllText(jsonFilePath);
                dynamic config = JsonConvert.DeserializeObject(json);
                string missionchiefPath = Path.Combine((string)config.Missionchief, "missionchief");
                if (config.Missionchief != null && Directory.Exists(missionchiefPath))
                {
                    InstallButton.Content = "Start";
                }
            }
        }
    }
}
