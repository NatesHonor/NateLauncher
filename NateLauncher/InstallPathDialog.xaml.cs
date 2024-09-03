using System.Windows;

namespace NateLauncher
{
    public partial class InstallPathDialog : Window
    {
        public InstallPathDialog()
        {
            InitializeComponent();
        }

        private void BrowseButton_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new System.Windows.Forms.FolderBrowserDialog();
            dialog.SelectedPath = PathTextBox.Text;
            System.Windows.Forms.DialogResult result = dialog.ShowDialog();

            if (result == System.Windows.Forms.DialogResult.OK)
            {
                string selectedPath = dialog.SelectedPath;
                if (selectedPath.Length > 30)
                {
                    PathTextBox.Text = selectedPath.Substring(0, 27) + "...";
                }
                else
                {
                    PathTextBox.Text = selectedPath;
                }
            }
        }

        private void OKButton_Click(object sender, RoutedEventArgs e)
        {
            this.DialogResult = true;
            this.Close();
        }
    }
}
