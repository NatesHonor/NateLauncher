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
                        string tempFolderPath = Path.Combine((string)config.Missionchief, "missionchief", "temp");
                        string installerPath = Path.Combine(tempFolderPath, "Windows-Installer.exe");

                        if (Directory.Exists(tempFolderPath) && File.Exists(installerPath))
                        {
                            Process.Start(installerPath);
                            return;
                        }
                    }
                    catch (JsonReaderException ex)
                    {
                        MessageBox.Show($"JSON parsing error: {ex.Message}");
                        Log($"JSON parsing error: {ex.Message}");
                        return;
                    }
                }

                MessageBox.Show("Installer not found.");
                return;
            }

            var dialog = new InstallPathDialog();
            dialog.PathTextBox.Text = @"C:\Program Files (x86)\Nate Launcher";
            if (dialog.ShowDialog() == true)
            {
                string installPath = dialog.PathTextBox.Text;
                await Utils.CheckAndRunInstaller(installPath, program);

                InstallButton.Content = "Start";
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
                    string missionchiefPath = Path.Combine((string)config.Missionchief, "missionchief");
                    if (config.Missionchief != null && Directory.Exists(missionchiefPath))
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
