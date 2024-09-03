using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;

namespace NateLauncher
{
    public static class Program
    {
        public static async Task Main(string[] args)
        {
            if (args.Length < 2)
            {
                Console.WriteLine("Usage: NateLauncherElevated <program> <path>");
                return;
            }

            string program = args[0];
            string path = args[1];

            await InstallProgram(program, path);
        }

        public static async Task InstallProgram(string program, string path)
        {
            if (string.IsNullOrEmpty(program))
            {
                Console.WriteLine("Usage: NateLauncherElevated <program> <path>");
                return;
            }

            if (program == "missionchief")
            {
                string url = "https://github.com/NatesHonor/MissionchiefBotInstaller/releases/latest/download/Windows-Installer.exe";
                string downloadPath = Path.Combine(path, "missionchief", "temp", "Windows-Installer.exe");

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
                            Console.WriteLine("Download successful.");
                        }
                        else
                        {
                            Console.WriteLine("Download failed.");
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"An error occurred: {ex.Message}");
                }
            }
            else
            {
                Console.WriteLine("Unknown program specified.");
            }
        }
    }
}
