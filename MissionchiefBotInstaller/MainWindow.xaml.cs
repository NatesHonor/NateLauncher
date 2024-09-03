using System;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Threading.Tasks;
using System.Windows;
using Newtonsoft.Json.Linq;

namespace MissionChiefBotInstaller
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private async void InstallButton_Click(object sender, RoutedEventArgs e)
        {
            string server = ServerTextBox.Text.ToLower();
            string email = EmailTextBox.Text;
            string password = PasswordBox.Password;

            if (string.IsNullOrEmpty(server) || string.IsNullOrEmpty(email) || string.IsNullOrEmpty(password))
            {
                MessageBox.Show("Please fill in all fields.");
                return;
            }

            string apiUrl = server == "na" ? "https://api.github.com/repos/NatesHonor/MissionchiefBot/releases/latest" :
                            server == "eu" ? "https://api.github.com/repos/NatesHonor/MissionchiefBotEU/releases/latest" : null;

            if (apiUrl == null)
            {
                MessageBox.Show("Invalid server. Please enter either 'na' or 'eu'.");
                return;
            }

            try
            {
                using (HttpClient client = new HttpClient())
                {
                    client.DefaultRequestHeaders.Add("Accept", "application/vnd.github.v3+json");
                    client.DefaultRequestHeaders.Add("User-Agent", "MissionChiefBotInstaller");

                    HttpResponseMessage response = await client.GetAsync(apiUrl);
                    response.EnsureSuccessStatusCode();

                    string json = await response.Content.ReadAsStringAsync();
                    JObject data = JObject.Parse(json);
                    string zipUrl = data["zipball_url"].ToString();

                    response = await client.GetAsync(zipUrl);
                    response.EnsureSuccessStatusCode();

                    byte[] zipBytes = await response.Content.ReadAsByteArrayAsync();
                    string tempPath = Path.Combine(Path.GetTempPath(), "MissionchiefBot.zip");

                    File.WriteAllBytes(tempPath, zipBytes);

                    string extractPath = Path.Combine(Environment.CurrentDirectory, "Bot");
                    Directory.CreateDirectory(extractPath);

                    ZipFile.ExtractToDirectory(tempPath, extractPath);

                    string extractedFolder = Directory.GetDirectories(extractPath)[0];
                    foreach (string file in Directory.GetFiles(extractedFolder))
                    {
                        File.Move(file, Path.Combine(extractPath, Path.GetFileName(file)));
                    }

                    Directory.Delete(extractedFolder, true);
                    File.Delete(tempPath);

                    string configPath = Path.Combine(extractPath, "config.ini");
                    using (StreamWriter writer = new StreamWriter(configPath))
                    {
                        writer.WriteLine("[credentials]");
                        writer.WriteLine($"username={email}");
                        writer.WriteLine($"password={password}");
                        writer.WriteLine("[client]");
                        writer.WriteLine("headless=true");
                        writer.WriteLine("[missions]");
                        writer.WriteLine("should_wait_before_missions=true");
                        writer.WriteLine("should_wait_before_missions_time=5");
                        writer.WriteLine("[transport]");
                        writer.WriteLine("should_handle_transport_requests=true");
                        writer.WriteLine("should_handle_transport_requests_time=60");
                        writer.WriteLine("prisoner_van_handling=false");
                        writer.WriteLine("minimum_prisoners=3");
                        writer.WriteLine("[dispatches]");
                        writer.WriteLine("dispatch_type=alliance");
                        writer.WriteLine("[other]");
                        writer.WriteLine("daily_login=true");
                        writer.WriteLine("claim_tasks=true");
                        writer.WriteLine("claim_tasks_time=5");
                        writer.WriteLine("event_calender=true");
                    }

                    MessageBox.Show("Installation complete.");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"An error occurred: {ex.Message}");
            }
        }

        private void UpdateButton_Click(object sender, RoutedEventArgs e)
        {
            // Implement update logic here
        }

        private void DashboardButton_Click(object sender, RoutedEventArgs e)
        {
            // Implement dashboard installation logic here
        }
    }
}
