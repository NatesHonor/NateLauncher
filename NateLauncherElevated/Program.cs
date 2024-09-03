using System;
using System.IO;
using System.IO.Compression;
using System.IO.Pipes;
using System.Net.Http;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Linq;

namespace NateLauncherElevated
{
    class Program
    {
        [DllImport("kernel32.dll")]
        static extern IntPtr GetConsoleWindow();

        [DllImport("user32.dll")]
        static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        const int SW_HIDE = 0;

        static async Task Main(string[] args)
        {
            var handle = GetConsoleWindow();
            ShowWindow(handle, SW_HIDE);

            if (args.Length < 1)
            {
                ReportError("Usage: ElevatedInstaller <action> [args...]");
                return;
            }

            string action = args[0];
            string[] actionArgs = args.Skip(1).ToArray();

            try
            {
                switch (action)
                {
                    case "ReadFile":
                        if (actionArgs.Length < 1) return;
                        string filePath = actionArgs[0];
                        ReadFile(filePath);
                        break;

                    case "InstallProgram":
                        if (actionArgs.Length < 2) return;
                        string program = actionArgs[0];
                        string installPath = actionArgs[1];
                        await InstallProgram(program, installPath);
                        break;

                    default:
                        ReportError("Unknown action specified.");
                        break;
                }
            }
            catch (Exception ex)
            {
                ReportError($"An error occurred: {ex.Message}");
            }
        }

        private static async Task InstallProgram(string program, string path)
        {
            string jsonFilePath = Path.Combine(path, "Nate Launcher.json");
            string jsonContent = $"{{\"Missionchief\": \"{path}\"}}";

            try
            {
                File.WriteAllText(jsonFilePath, jsonContent);
                ReportSuccess("JSON file saved successfully.");
                if (program == "missionchief")
                {
                    string url = "https://github.com/NatesHonor/MissionchiefBot/releases/latest";
                    string downloadPath = Path.Combine(path, "sourcecode.zip");
                    string extractPath = path;

                    using (HttpClient client = new HttpClient())
                    {
                        HttpResponseMessage response = await client.GetAsync(url);
                        response.EnsureSuccessStatusCode();
                        string actualUrl = response.RequestMessage.RequestUri.ToString();
                        string version = actualUrl.Split('/').Last();
                        string downloadUrl = $"https://github.com/NatesHonor/MissionchiefBot/archive/refs/tags/{version}.zip";

                        byte[] fileBytes = await client.GetByteArrayAsync(downloadUrl);
                        File.WriteAllBytes(downloadPath, fileBytes);

                        if (File.Exists(downloadPath))
                        {
                            if (Directory.Exists(extractPath))
                            {
                                Directory.Delete(extractPath, true);
                            }

                            Directory.CreateDirectory(extractPath);
                            ZipFile.ExtractToDirectory(downloadPath, extractPath);

                            string extractedFolderPath = Directory.GetDirectories(extractPath).FirstOrDefault();
                            string finalFolderPath = Path.Combine(extractPath, "MissionchiefBot");

                            if (extractedFolderPath != null && Directory.Exists(extractedFolderPath))
                            {
                                Directory.Move(extractedFolderPath, finalFolderPath);
                                ReportSuccess("Download, rename, and extraction successful!");
                            }
                            else
                            {
                                ReportError("Extraction failed.");
                            }
                        }
                        else
                        {
                            ReportError("Download failed.");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                ReportError($"An error occurred during installation: {ex.Message}");
            }
        }

        private static void ReadFile(string filePath)
        {
            try
            {
                string content = File.ReadAllText(filePath);
                ReportSuccess($"File content: {content}");
            }
            catch (Exception ex)
            {
                ReportError($"Failed to read file: {ex.Message}");
            }
        }

        private static void ReportError(string message)
        {
            Log($"Error: {message}");
            SendMessage($"Error: {message}");
        }

        private static void ReportSuccess(string message)
        {
            Log($"Success: {message}");
            SendMessage($"Success: {message}");
        }

        private static void SendMessage(string message)
        {
            try
            {
                using (var client = new NamedPipeClientStream("NateLauncherPipe"))
                {
                    client.Connect(5000);
                    using (var writer = new StreamWriter(client))
                    {
                        writer.AutoFlush = true;
                        writer.WriteLine(message);
                    }
                }
            }
            catch (UnauthorizedAccessException uaEx)
            {
                ReportError($"Access denied when trying to send message: {uaEx.Message}");
            }
            catch (IOException ioEx)
            {
                ReportError($"I/O error when trying to send message: {ioEx.Message}");
            }
            catch (Exception ex)
            {
                ReportError($"Failed to send message: {ex.Message}");
            }
        }

        private static void Log(string message)
        {
            string logFilePath = @"C:\Program Files (x86)\Nate Launcher\logs\NateLauncherElevated.log";
            string logDirectory = Path.GetDirectoryName(logFilePath);

            try
            {
                if (!Directory.Exists(logDirectory))
                {
                    Directory.CreateDirectory(logDirectory);
                }
                using (FileStream fs = new FileStream(logFilePath, FileMode.Append, FileAccess.Write, FileShare.None))
                using (StreamWriter sw = new StreamWriter(fs))
                {
                    sw.WriteLine($"{DateTime.Now}: {message}");
                }
            }
            catch (UnauthorizedAccessException ex)
            {
                Console.WriteLine($"Logging failed: {ex.Message}");
            }
            catch (IOException ex)
            {
                Console.WriteLine($"Logging failed: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Logging failed: {ex.Message}");
            }
        }
    }
}
