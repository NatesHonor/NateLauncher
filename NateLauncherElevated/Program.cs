using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace NateLauncher
{
    public static class Program
    {
        private static readonly string LogDirectory = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "logs");
        private static readonly string LogFilePath = Path.Combine(LogDirectory, "NateLauncherElevated.log");

        public static async Task Main(string[] args)
        {
            if (args.Length < 2)
            {
                Log("Usage: NateLauncherElevated <program> <path>");
                return;
            }

            string program = args[0];
            string path = args[1];

            try
            {
                Log("Starting configuration file creation.");
                CreateOrUpdateConfigFile(path, program);
                Log("Configuration file created or updated.");

                Log("Starting program installation.");
                await InstallProgram(program, path);
                Log("Program installation completed.");
            }
            catch (Exception ex)
            {
                Log($"An error occurred: {ex.Message}");
            }
        }

        private static void CreateOrUpdateConfigFile(string path, string program)
        {
            string jsonFilePath = Path.Combine(path, "Nate Launcher.json");

            JObject config = new JObject();

            if (File.Exists(jsonFilePath))
            {
                string json = File.ReadAllText(jsonFilePath);
                config = JObject.Parse(json);
            }

            if (!config.ContainsKey("missionchief"))
            {
                config["missionchief"] = new JObject();
            }

            config["missionchief"]["path"] = path;
            config["missionchief"]["installed"] = true;

            File.WriteAllText(jsonFilePath, config.ToString());
            Log("Configuration file written to disk.");
        }

        public static async Task InstallProgram(string program, string path)
        {
            if (string.IsNullOrEmpty(program))
            {
                Log("Usage: NateLauncherElevated <program> <path>");
                return;
            }

            if (program == "missionchief")
            {
                string url = "https://api.natemarcellus.com/download/MissionchiefBotInstaller.exe";
                string downloadPath = Path.Combine(path, "missionchief", "temp", "MissionchiefBotInstaller.exe");

                try
                {
                    using (HttpClient client = new HttpClient())
                    {
                        HttpResponseMessage response = await client.GetAsync(url);
                        response.EnsureSuccessStatusCode();

                        byte[] fileBytes = await response.Content.ReadAsByteArrayAsync();
                        Directory.CreateDirectory(Path.GetDirectoryName(downloadPath));
                        File.WriteAllBytes(downloadPath, fileBytes);

                        if (File.Exists(downloadPath))
                        {
                            Log("Download successful.");
                        }
                        else
                        {
                            Log("Download failed.");
                        }
                    }
                }
                catch (Exception ex)
                {
                    Log($"An error occurred: {ex.Message}");
                }
            }
            else
            {
                Log("Unknown program specified.");
            }
        }

        private static void Log(string message)
        {
            Directory.CreateDirectory(LogDirectory);
            File.AppendAllText(LogFilePath, $"{DateTime.Now}: {message}{Environment.NewLine}");
        }
    }
}
