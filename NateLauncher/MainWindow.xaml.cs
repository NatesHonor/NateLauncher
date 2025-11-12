using Newtonsoft.Json;
using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media.Imaging;

namespace NateLauncher
{
    public partial class MainWindow : Window
    {
        private const string PipeName = "NateLauncherPipe";

        public MainWindow()
        {
            InitializeComponent();
            Task.Run(() => PipeListener.ListenForMessages(PipeName));
            Log("MainWindow initialized.");
            CheckInstallStatus();
        }

        private void GearIcon_Click(object sender, MouseButtonEventArgs e)
        {
            MessageBox.Show("Settings clicked!");
            Log("Settings clicked.");
        }

        private void MissionchiefButton_Click(object sender, RoutedEventArgs e)
        {
            AppListView.Visibility = Visibility.Collapsed;
            MissionchiefView.Visibility = Visibility.Visible;
        }

        private void MissionchiefButton_MouseEnter(object sender, MouseEventArgs e)
        {
            WpfAnimatedGif.ImageBehavior.SetAnimatedSource(MissionchiefImage, new BitmapImage(new Uri("pack://application:,,,/Resources/missionchief_hover.gif")));
        }

        private void MissionchiefButton_MouseLeave(object sender, MouseEventArgs e)
        {
            WpfAnimatedGif.ImageBehavior.SetAnimatedSource(MissionchiefImage, new BitmapImage(new Uri("pack://application:,,,/Resources/missionchief.png")));
        }

        private void BackButton_Click(object sender, RoutedEventArgs e)
        {
            MissionchiefView.Visibility = Visibility.Collapsed;
            AppListView.Visibility = Visibility.Visible;
        }

        private async void InstallButton_Click(object sender, RoutedEventArgs e)
        {
            Log("Install button clicked.");
            string program = "missionchief";

            if (InstallButton.Content.ToString() == "Start")
            {
                string jsonFilePath = @"C:\Program Files (x86)\Nate Launcher\Nate Launcher.json";
                if (File.Exists(jsonFilePath))
                {
                    string json = Utils.ReadFileWithAdminCheck(jsonFilePath);
                    if (string.IsNullOrEmpty(json))
                    {
                        MessageBox.Show("Failed to read the JSON configuration.");
                        Log("Failed to read the JSON configuration.");
                        return;
                    }

                    try
                    {
                        dynamic config = JsonConvert.DeserializeObject(json);
                        string missionchiefPath = (string)config?.missionchief?.path;
                        bool isInstalled = (bool)config?.missionchief?.installed;

                        if (string.IsNullOrEmpty(missionchiefPath) || !isInstalled)
                        {
                            MessageBox.Show("Missionchief is not installed or path is missing in the configuration.");
                            Log("Missionchief is not installed or path is missing in the configuration.");
                            return;
                        }

                        string tempFolderPath = Path.Combine(missionchiefPath, "missionchief", "temp");
                        string installerPath = Path.Combine(tempFolderPath, "MissionchiefBotInstaller.exe");

                        if (Directory.Exists(tempFolderPath) && File.Exists(installerPath))
                        {
                            Process.Start(installerPath);
                            return;
                        }
                        else
                        {
                            MessageBox.Show("Installer file not found.");
                            Log("Installer file not found.");
                        }
                    }
                    catch (JsonReaderException ex)
                    {
                        MessageBox.Show($"JSON parsing error: {ex.Message}");
                        Log($"JSON parsing error: {ex.Message}");
                    }
                }
                else
                {
                    MessageBox.Show("Configuration file does not exist.");
                    Log("Configuration file does not exist.");
                }

                return;
            }

            var dialog = new InstallPathDialog();
            dialog.PathTextBox.Text = @"C:\Program Files (x86)\Nate Launcher";
            if (dialog.ShowDialog() == true)
            {
                string installPath = dialog.PathTextBox.Text;
                bool installResult = await Utils.CheckAndRunInstaller(installPath, program);
                if (!installResult)
                {
                    MessageBox.Show("Failed to install. Administrator permissions might be required.");
                    Log("Failed to install due to insufficient permissions.");
                }
                else
                {
                    Log("Installation completed successfully.");
                    InstallButton.Content = "Start";
                }
            }
        }

        private void Log(string message)
        {
            Debug.WriteLine(message);
        }

        private void CheckInstallStatus()
        {
            string jsonFilePath = @"C:\Program Files (x86)\Nate Launcher\Nate Launcher.json";
            if (File.Exists(jsonFilePath))
            {
                string json = Utils.ReadFileWithAdminCheck(jsonFilePath);
                if (string.IsNullOrEmpty(json))
                {
                    MessageBox.Show("Failed to read the JSON configuration.");
                    Log("Failed to read the JSON configuration.");
                    return;
                }

                try
                {
                    dynamic config = JsonConvert.DeserializeObject(json);
                    bool isMissionchiefInstalled = config?.missionchief?.installed ?? false;
                    if (isMissionchiefInstalled)
                    {
                        InstallButton.Content = "Start";
                    }
                }
                catch (JsonReaderException ex)
                {
                    MessageBox.Show($"JSON parsing error: {ex.Message}");
                    Log($"JSON parsing error: {ex.Message}");
                }
            }
        }

        private void Window_StateChanged(object sender, EventArgs e)
        {
            if (this.WindowState == WindowState.Maximized)
            {
                this.WindowState = WindowState.Normal;
                Log("Window state changed to normal.");
            }
        }
    }
}
