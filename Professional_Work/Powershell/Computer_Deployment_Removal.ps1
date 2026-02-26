# Device Array
$devices = "" # <--- Put devices you would like to remove deployments for here

# Loop through and display deployment count for each device
foreach ($device in $devices) {
    $applications = Get-CMDeployment -CollectionName $device -FeatureType Application
    $count = $applications.Count
    Write-Output "Application deployments found for $device : $count"
}

# See if user would like to delete deployments per device or all devices
$prompt = "`nWould you like to delete deployments for all devices or choose for each device [All/Indiv]?"
do {
    $response = Read-Host -Prompt $prompt
} until ($repsone -eq 'all' -or $response -eq 'All' -or $response -eq 'indiv' -or $response -eq 'Indiv')

# See if response is all
if ($response -eq 'all' -or $response -eq 'All') {

    # Ask for Confirmation to delete all deployments
    $prompt = "`nAre you sure you wish to delete all application deployments [Y/N]?"
    do {
        $response = Read-Host -Prompt $prompt
    } until ($repsone -eq 'y' -or $response -eq 'Y' -or $response -eq 'n' -or $response -eq 'N')

    # Go forward with deletion if response is yes
    if ($response -eq 'y' -or $response -eq 'Y') {

        # Loop through each test computer and remove deployments
        foreach ($device in $devices) {
            deleteDeployments -device $device
        }
    } else {
        Write-Host "Aborting Application Deployment Deletion"
    }

} else {
    # Go through each device individually and ask about deletion

    # Loop through each test computer and remove deployments
    foreach ($device in $devices) {
        $deployments = Get-CMDeployment -CollectionName $device -FeatureType Application

        # Check if more than one deployment
        if ($deployments.Count -gt 0)
        {
            $prompt = "`nWould you like to delete all application deployments for $device [Y/N]?"
            do {
                $response = Read-Host -Prompt $prompt
            } until ($repsone -eq 'y' -or $response -eq 'Y' -or $response -eq 'n' -or $response -eq 'N')

            # Go forward with deletion if response is yes
            if ($response -eq 'y' -or $response -eq 'Y') {
                # call deletion function
                deleteDeployments -device $device
            }
        } else {
         Write-Output "Skipping $device due to no deployments found"
         }
    }
}

#function for deleting deployments
function deleteDeployments {
    param (
        [string]$device
        )

    # Get all deployments targeting this collection
    $deployments = Get-CMDeployment -CollectionName $device -FeatureType Application

    # Check if device has any deployments
    if ($deployments.Count -eq 0) {
        Write-Host "No deployments found for device $($device)"
    } else {
        Write-Host "Removing Deployments for Device: $($device)"
        # Loop through each deployment and delete
        foreach ($deployment in $deployments) {
            Write-Host "Removing deployment: $($deployment.SoftwareName) ($($deployment.DeploymentID))"

            # attempt to remove deployment
            try {
                Remove-CMDeployment -DeploymentId $deployment.DeploymentID -ApplicationName $deployment.ApplicationName -Force
                Write-Host "Removed successfully."
            } catch {
                Write-Warning "Failed to remove deployment $($deployment.DeploymentID): $_"
            }
        }
    }
}
