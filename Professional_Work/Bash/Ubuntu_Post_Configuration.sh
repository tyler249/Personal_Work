# Code below is part of a larger configuration script for Ubuntu setup
# on NAU computers. Below section is my contribution

# Script for grabbing and executing Defender, Cisco, KeyAccess, and Intune install
echo "Beginning post configuration installs"

# Get CIFS utilities
apt install -y cifs-utils

USER=$(logname)

# Define the server and mount point
SERVER=""
MOUNT_POINT="" 

# Create the mount point if it doesn't exist
mkdir -p "$MOUNT_POINT"

echo "Mounting the share as root..."

# Loop until share mounted correctly or user quits
while true; do

    # Grab current user's username and password for share
    echo -n "Enter your NAU userID (abc123): " > /dev/tty
	read USERNAME < /dev/tty

    # Check if the user wants to quit
    if [ "$USERNAME" == "exit" ]; then
        echo "Exiting the script."
        break
    fi

    mount -t cifs "$SERVER" "$MOUNT_POINT" -o username=$USERNAME,domain=NAU

    # Check for successful mounting
    if [ $? -eq 0 ]; then
        echo "Successfully mounted the share at $MOUNT_POINT"

        SHARE="/mnt/software/Linux"
        DESKTOP="/home/$USER/Desktop/"

        # Copy down Microsoft Defender
        echo "Grabbing Microsoft Defender"
        cp -r "$SHARE/Windows Defender" $DESKTOP

        # Get path to newest KeyConfigure folder
        NEWEST=$(ls -1 "$SHARE/KeyConfigure" | sort -V | tail -n 1)

        # Show KeyConfigure version
        echo "Grabbing KeyAccess version $NEWEST"

        # Copy down KeyConfigure
        cp -r $SHARE/KeyConfigure/$NEWEST $DESKTOP

        # Make directory for Cisco Secure Connect
        mkdir -p "$DESKTOP/Cisco"

        # Get path to newest Cisco tar file for current system archtype
        echo "Determining system archtype for Cisco Secure Connect"
        if [ "$(uname -m)" = "aarch64" ]; then
            echo "Archtype is aarch64"
            NEWEST_FILE=$(ls -1 "$SHARE/Cisco Secure" | grep -E '^cisco-secure-client-linux-arm64-.*-k9\.tar$' | sort -V | tail -n 1)
        elif [ "$(uname -m)" = "x86_64" ]; then
            echo "Archtype is x86_64"
            NEWEST_FILE=$(ls -1 "$SHARE/Cisco Secure" | grep -E '^cisco-secure-client-linux64-.*-k9\.tar$' | sort -V | tail -n 1)
        else
            echo "Unknown architecture: $(uname -m)"
            exit 1
        fi

        # Copy down Cisco Secure files
        echo "Grabbing Cisco Secure files"
        cp -r "$SHARE/Cisco Secure/cisco_connect_install.sh" $DESKTOP/Cisco
        cp -r "$SHARE/Cisco Secure/$NEWEST_FILE" $DESKTOP/Cisco

        # Copy down Intune files
        echo "Grabbing Intune files"
        cp -r "$SHARE/Intune and Edge" $DESKTOP

        # Begin installation of each service
        # Microsoft Defender Install
        echo "Beginning Install of Microsoft Defender" > /dev/tty
		echo "Starting Microsoft Defender Install"

		# set working directory
		WORKING_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
		
		# Go into Windows Defender folder
		cd "Windows Defender" 

		# Make script executable
		chmod +x mde_installer.sh

		# Start Defender install
		./mde_installer.sh -i -s -o MicrosoftDefenderATPOnboardingLinuxServer.py

		# Check if install successfull
		if [ "$(mdatp health | grep "healthy" | awk '{print $3}')" == "true" ]; then
			echo "Install of Microsft Defender Successful" > /dev/tty
		else
			echo "Install of Microsoft Defender Failed" > /dev/tty
		fi

		cd ..
    

        # Cisco Secure Install
        echo -n "Would you like to install Cisco Secure Connect? (Y/N): " > /dev/tty
		read response < /dev/tty
        case $response in 
        [Yy])
            echo "Starting Cisco Secure Connect Install"

            # set working directory
            WORKING_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
            
            # Go into Cisco folder
            cd "Cisco" 

            # Make script executable
            chmod +x cisco_connect_install.sh

            # Start Cisco install
            ./cisco_connect_install.sh

			# Check if install successful
			if [ -d "/opt/cisco" ]; then
				echo "Cisco Secure Connect installed successfully" > /dev/tty
			else
				echo "Cisco Secure Connect failed to install" > /dev/tty
			fi

            cd ..
            ;;
        [Nn]) 
            echo "No selected: Install Aborted"
            ;;
        *)
            echo "Invalid Input: Install Aborted"
            ;;
        esac

        # Intune Install
        echo -n "Would you like to install Microsoft Intune? (Y/N): " > /dev/tty
		read response < /dev/tty
        case $response in 
        [Yy])
            echo "Starting Intune Install"

            # set working directory
            WORKING_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
            
            # Go into Intune folder
            cd "Intune and Edge" 

            # Make script executable
            chmod +x intune_and_edge_fix.sh

            # Start Intune install
            ./intune_and_edge_fix.sh

			# Check if install successful
			if [ -d "/opt/microsoft/intune" ]; then
				echo "Microsoft Intune installed successfully" > /dev/tty
			else
				echo "Micrsoft Intune failed to install" > /dev/tty
			fi

            cd ..
            ;;
        [Nn]) 
            echo "No selected: Install Aborted"
            ;;
        *)
            echo "Invalid Input: Install Aborted"
            ;;
        esac

        # KeyAccess Install
        echo -n "Would you like to install KeyAccess? (Y/N): " > /dev/tty
		read response < /dev/tty
        case $response in 
        [Yy])
            echo "Starting KeyAccess Install"

            # set working directory
            WORKING_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
            
            # Go into KeyAccess folder
            cd "$NEWEST" 

            # Make script executable
            chmod +x KeyAccess_Install.sh

            # Start KeyAcess install
            ./KeyAccess_Install.sh

			# Check if install successful
			if [ -x "/usr/bin/kasetup" ]; then
				echo "KeyAccess installed successfully" > /dev/tty
			else
				echo "KeyAccess failed to install" > /dev/tty
			fi

            cd ..
            ;;
        [Nn]) 
            echo "No selected: Install Aborted"
            ;;
        *)
            echo "Invalid Input: Install Aborted"
            ;;
        esac

        # Remove folders once done
        echo "Installs complete, removing installers"
        rm -rf $DESKTOP/$NEWEST
        rm -rf "$DESKTOP/Windows Defender"
        rm -rf $DESKTOP/Cisco 
        rm -rf "$DESKTOP/Intune and Edge"

        # Exit loop
        break
    else
        echo "Failed to mount the share. Type 'exit' for username if you wish to abort post configuration" > /dev/tty
    fi
done

echo -n "Script finished, reboot required. Reboot Now? (Y/N): " > /dev/tty
read response < /dev/tty
case $response in
[Yy])
	reboot
	;;
[Nn])
	;;
*)
	;;
esac