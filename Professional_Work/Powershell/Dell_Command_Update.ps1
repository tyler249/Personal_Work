# Start job
$job = Start-Job -ScriptBlock {
    param($DcuCliPath, $EncryptedPasswordFile, $EncryptionKey, $OutputLogFile)
    $proc = Start-Process -FilePath $DcuCliPath `
        -ArgumentList "/applyupdates", "-encryptedPassword=`"$using:tempkey`"", "-encryptionKey=`"$EncryptionKey`"", "-outputLog=`"$OutputLogFile`"" `
        -WindowStyle Hidden -PassThru -Wait
    return $proc.ExitCode
} -ArgumentList $DcuCliPath, $EncryptedPasswordFile, $EncryptionKey, $OutputLogFile

# Wait for completion using the job object directly
while ($job.State -ne 'Completed' -and $job.State -ne 'Failed') {
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 200
}