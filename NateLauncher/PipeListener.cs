using System;
using System.Diagnostics;
using System.IO;
using System.IO.Pipes;
using System.Threading.Tasks;
using System.Windows;

namespace NateLauncher
{
    public static class PipeListener
    {
        public static async Task ListenForMessages(string pipeName)
        {
            while (true)
            {
                try
                {
                    using (var server = new NamedPipeServerStream(pipeName, PipeDirection.In, 1, PipeTransmissionMode.Message, PipeOptions.Asynchronous))
                    {
                        Debug.WriteLine("Waiting for connection...");
                        await server.WaitForConnectionAsync();
                        Debug.WriteLine("Named pipe server connected.");

                        using (var reader = new StreamReader(server))
                        {
                            while (server.IsConnected)
                            {
                                try
                                {
                                    string message = await reader.ReadLineAsync();
                                    if (message != null)
                                    {
                                        Application.Current.Dispatcher.Invoke(() => MessageBox.Show(message));
                                        Debug.WriteLine($"Message received: {message}");
                                    }
                                }
                                catch (Exception ex)
                                {
                                    Debug.WriteLine($"Error reading from pipe: {ex.Message}");
                                }
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"Error with pipe server: {ex.Message}");
                }

                await Task.Delay(1000);
            }
        }
    }
}
