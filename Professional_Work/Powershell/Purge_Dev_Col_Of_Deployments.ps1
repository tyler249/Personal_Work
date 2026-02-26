# Specify the target collection name
$collectionName = $null # <-- change this to the collection you wish to purge

# Get the collection object
$collection = Get-CMDeviceCollection -Name $collectionName

if (-not $collection) {
    Write-Error "Collection '$collectionName' not found."
    exit
}

# Get all deployments targeting this collection
$deployments = Get-CMDeployment -CollectionName $collectionName -FeatureType Application

if ($deployments.Count -eq 0) {
    Write-Host "No deployments found for collection '$collectionName'."
} else {
    foreach ($deployment in $deployments) {
        Write-Host "Removing deployment: $($deployment.SoftwareName) ($($deployment.DeploymentID))"

        try {
            Remove-CMDeployment -DeploymentId $deployment.DeploymentID -ApplicationName $deployment.ApplicationName -Force
            Write-Host "Removed successfully."
        } catch {
            Write-Warning "Failed to remove deployment $($deployment.DeploymentID): $_"
        }
    }
}
