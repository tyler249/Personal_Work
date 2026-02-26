# For security purposes, this script was trasformed into and exe to avoid password leaking

# Load the required assembly for Windows Forms
Add-Type -AssemblyName System.Windows.Forms

# Define variables
$EncryptionKey = ""
$BiosPassword = ""
$EncryptedPasswordFile = "C:\Temp\encrypted_password.txt"
$OutputLogFile = "C:\Temp\DCUoutput.log"
$DcuCliPath = "C:\Program Files (x86)\Dell\CommandUpdate\dcu-cli.exe"

# Create the form
$form = New-Object System.Windows.Forms.Form
$form.Text = "Dell Command Update"
$form.Width = 400
$form.Height = 200

# Create a button
$button = New-Object System.Windows.Forms.Button
$button.Text = "Check for Updates"
$button.Width = 150
$button.Height = 50
$button.Top = 60
$button.Left = 125

# Add button click event handler
$button.Add_Click({
    # Ensure the directory for the encrypted password file exists
    $EncryptedPasswordFileDirectory = [System.IO.Path]::GetDirectoryName($EncryptedPasswordFile)
    if (-not (Test-Path -Path $EncryptedPasswordFileDirectory)) {
        New-Item -Path $EncryptedPasswordFileDirectory -ItemType Directory -Force | Out-Null
    }

    # Generate Encrypted BIOS Password
    Start-Process -FilePath $DcuCliPath -Wait -ArgumentList "/generateEncryptedPassword", "-encryptionKey=`"$EncryptionKey`"", "-password=`"$BiosPassword`"", "-outputPath=`"$EncryptedPasswordFile`""

    # Check if the file was created and read its content
    if (Test-Path -Path $EncryptedPasswordFile) {
        try {
            # Use Get-ChildItem to confirm file existence
            $file = Get-ChildItem -Path $EncryptedPasswordFile -File
            Write-Output "File found: $($file.FullName)"
            
            # Read the encrypted password from the file
            $tempkey = Get-Content -Path $file.FullName -Raw
            Write-Output "Encrypted password read successfully."

            # Apply BIOS Updates
            $process = Start-Process -FilePath $DcuCliPath -ArgumentList "/applyupdates", "-encryptedPassword=`"$tempkey`"", "-encryptionKey=`"$EncryptionKey`"", "-outputLog=`"$OutputLogFile`"" -PassThru -Wait
            $exitCode = $process.ExitCode

            # Read the output log to verify results
            $logContent = Get-Content -Path $OutputLogFile -Raw
            if ($logContent -match "No updates available") {
                $message = "No updates available."
            } elseif ($exitCode -eq 500) {
                $message = "No updates were found the system is up to date."
            } elseif ($exitCode -eq 1) {
                $message = "Dell Updates were applied and a restart is required to complete the installation."
            } elseif ($exitCode -eq 0) {
                $message = "Dell updates applied successfully"
            }else {
                $message = "There might be a error return with exit code: $exitCode"
            }

            # Show the result in a message box
            [System.Windows.Forms.MessageBox]::Show($message, "Dell Command Update Status", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)

        } catch {
            # Show error message
            $errorMessage = "Failed to read the encrypted password or apply updates: $_"
            [System.Windows.Forms.MessageBox]::Show($errorMessage, "Dell Command Update Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        }
    } else {
        # Show error message
        $errorMessage = "Failed to generate encrypted BIOS password. File not found: $EncryptedPasswordFile"
        [System.Windows.Forms.MessageBox]::Show($errorMessage, "Dell Command Update Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    }
})

# Add the button to the form
$form.Controls.Add($button)

# Show the form
$form.ShowDialog()
