#!/bin/bash
# This script resets the secure token on Mac when a users resets their password 
# and runs into issues

# REQUIREMENTS
# Must have admin/LAPS password and User credentials

# START
# List every user with a secure token
users=$(dscl . -list /Users | while read user; do
        dscl . -read /Users/"$user" OriginalNodeName 2>/dev/null | grep -q "/Active Directory/" && echo "$user"
        done)

# Begin string for secure token users
secureTokenUsers=""

# loop through found users
for user in $users; do
    status=$(sudo sysadminctl -secureTokenStatus "$user" 2>&1)

    # check if token is enabled
    if [[ "$status" == *"ENABLED"* ]]; then
        # if enabled, add user to list 
        secureTokenUsers+="$user\n"
    fi
done

# ensure users in list
if [[ -z "$secureTokenUsers" ]]; then
    osascript -e 'display dialog "No mobile user accounts found." buttons {"OK"} default button "OK"'
    exit 1
fi

# format secureTokenUsers for osascript
userList=$(echo "$secureTokenUsers" | awk '{printf "\"%s\", ", $0}' | sed 's/, $//')

# get username of user to update secure token
userUsername=$(osascript -e "choose from list {$userList} with prompt \"Select a user:\"")

# check for user selected
if [[ -z "$userUsername" || "$userUsername" == "false" ]]; then
    osascript -e 'display dialog "Error: No user selected. Exiting program." buttons {"OK"} default button "OK"'
    exit 1
fi

# Get Admin Credentials (secure)
# osascript to get admin username
adminUsername=$(osascript -e 'Tell application "System Events" to display dialog "Enter username of admin account. Cannot be '$userUsername':" default answer "" buttons {"Cancel", "OK"} default button "OK"'  -e 'text returned of result')

# check is cancel clicked
if [ -z "$adminUsername" ]; then
    osascript -e 'display dialog "Error: Cancel button selected or no input. Exiting program." buttons {"OK"} default button "OK"'
    exit 1
fi

# osascript to get admin password
adminPassword=$(osascript -e 'Tell application "System Events" to display dialog "Enter the password for '$adminUsername':" default answer "" with hidden answer buttons {"Cancel", "OK"} default button "OK"'  -e 'text returned of result')

# check if cancel clicked
if [ -z "$adminPassword" ]; then
    osascript -e 'display dialog "Error: Cancel button selected or no input. Exiting program." buttons {"OK"} default button "OK"'
    exit 1
fi

# osascript to get user password
userPassword=$(osascript -e 'Tell application "System Events" to display dialog "Enter the password for '$userUsername':" default answer "" with hidden answer buttons {"Cancel", "OK"} default button "OK"'  -e 'text returned of result')

# check if cancel clicked
if [ -z "$userPassword" ]; then
    osascript -e 'display dialog "Error: Cancel button selected or no input. Exiting program." buttons {"OK"} default button "OK"'
    exit 1
fi

# Turn off secure token
sudo sysadminctl -adminUser "$adminUsername" -adminPassword "$adminPassword" -secureTokenOff "$userUsername" -password "$userPassword"


# Show Result
result=$(sudo sysadminctl -secureTokenStatus "$userUsername" 2>&1)
osascript -e "display dialog \"$result\" buttons {\"OK\"} default button \"OK\""

# Turn on secure token 
sudo sysadminctl -adminUser "$adminUsername" -adminPassword "$adminPassword" -secureTokenOn "$userUsername" -password "$userPassword"

# Return Result
result=$(sudo sysadminctl -secureTokenStatus "$userUsername" 2>&1)
osascript -e "display dialog \"$result\" buttons {\"OK\"} default button \"OK\""

# Ask for reboot
RESPONSE=$(osascript -e 'display dialog "Would you like to reboot your computer now?" buttons {"Cancel", "Reboot"} default button "Reboot"' -e 'return button returned of result')

if [[ $RESPONSE == "Reboot" ]]; then
    sudo reboot
else
    osascript -e "display dialog \"Please reboot computer as soon as possible to verify user's ability to log in.\" buttons {\"OK\"} default button \"OK\""
fi

# End script
exit 0