using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Security.Principal;
using System.Threading.Tasks;
using System.Windows;
using MissionchiefBotInstaller;
using MissionchiefBotInstaller.InstallMethods;
using Newtonsoft.Json.Linq;

namespace MissionChiefBotInstaller
{
    public partial class MainWindow : Window
    {
        private readonly InstallButtonHandler installButtonHandler;

        public MainWindow()
        {
            InitializeComponent();
            string installPath = GetInstallPath();
            if (!string.IsNullOrEmpty(installPath))
            installButtonHandler = new InstallButtonHandler();
        }

        private string GetInstallPath()
        {
            string jsonFilePath = @"C:\Program Files (x86)\Nate Launcher\Nate Launcher.json";
            if (File.Exists(jsonFilePath))
            {
                string json = File.ReadAllText(jsonFilePath);
                JObject config = JObject.Parse(json);
                return config["missionchief"]?["path"]?.ToString();
            }
            return null;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            string dataPath = Path.Combine(Path.GetTempPath(), "MissionchiefBotInstallerData.json");
            if (File.Exists(dataPath))
            {
                string json = File.ReadAllText(dataPath);
                JObject data = JObject.Parse(json);

                ServerTextBox.Text = data["server"].ToString();
                EmailTextBox.Text = data["email"].ToString();
                PasswordBox.Password = data["password"].ToString();

                File.Delete(dataPath);
            }
        }

        private async void InstallButton_Click(object sender, RoutedEventArgs e)
        {
            string installDir = GetInstallPath();
            string server = ServerTextBox.Text.ToLower();
            string email = EmailTextBox.Text;
            string password = PasswordBox.Password;

            await installButtonHandler.InstallButton_Click(sender, e, installDir, server, email, password);
        }

        private void UpdateButton_Click(object sender, RoutedEventArgs e)
        {
        }

        private void DashboardButton_Click(object sender, RoutedEventArgs e)
        {
        }
    }
}
