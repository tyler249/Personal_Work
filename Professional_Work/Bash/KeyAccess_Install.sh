#!/bin/bash

# Key Access debfile
if [ "$(uname -m)" = "aarch64" ]; then
    debfile=$(ls KeyAccess_*_arm64.deb 2>/dev/null | head -n1)
elif [ "$(uname -m)" = "x86_64" ]; then
    debfile=$(ls KeyAccess_*_amd64.deb 2>/dev/null | head -n1)
else
    echo "Unknown architecture: $(uname -m)"
    exit 1
fi

debfileVersion=$(dpkg-deb -f $debfile Version)
echo "Script will use $debfile for install"

# log file path
log=/var/log/NAU/KeyAccess_Install.log
echo "Log can be found at /var/log/NAU/KeyAccess_Install.log"

# Make sure log exists
mkdir /var/log/NAU -p
touch $log

# Make echos and output go to log
exec 1>> $log

# Timestamp
ts() {
	date +"%m-%d-%y %l:%M:%S%p"
}

echo "~~~~ $(ts): Starting Script"

# Get current version of Key Access installed if any
version=$(dpkg -s keyaccess 2>/dev/null | awk -F': ' '/^Version:/ {print $2}')

# Display version found (blank means not installed)
echo "~~~~ $(ts): Current version: $version"

# Check if Key Access is not installed at all
if [[ -z "$version" ]]; then
    echo "~~~~ $(ts): Not Installed"
    echo "Not Installed, beginning Installation" >&2

    # Install main 
    env KA_SERVERHOST= dpkg -i $debfile

    # Install necessary modules
    apt-get install -y libcanberra-gtk-module

# Check if Key Access is already installed 
elif dpkg --compare-versions $version ge $debfileVersion; then
    echo "~~~~ $(ts): Key Access Already Installed"
    echo "Key Access Already Installed" >&2

# Otherwise assume  updated needed
else 
    echo "~~~~ $(ts): Update Needed"
    echo "Update Needed, beginning update process" >&2
    
    # Uninstall Current Version
    dpkg -r KeyAccess
    dpkg -p KeyAccess

    # Install Key Access
    env KA_SERVERHOST= dpkg -i $debfile

    # Install necessary modules
    apt-get install libcanberra-gtk-module
fi