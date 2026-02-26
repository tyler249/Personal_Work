import requests
 
JAMF = ""
#smart device group id (change to required group)
deviceGroupID = 117
 
def getAccessToken ():
    client_secret = {
                    "client_name":"",
                    "client_id":"",
                    "client_secret":"",
                    "grant_type":"client_credentials",
                    }
 
    response = requests.post(f'{JAMF}/api/v2/oauth/token', data=client_secret)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Unable to generate authentication token")
        exit
 
# get access token
access_token = getAccessToken()
 
# set up headers
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
 
# attempt to get computer group
try:
    # change smart-group-membership to static-group-membership or vice versa depending on group needed
    response = requests.get(f'{JAMF}/api/v1/mobile-device-groups/static-group-membership/{deviceGroupID}', headers=headers)
    response.raise_for_status()
except:
    print("Could not retreive computer group, aborting script")
    exit
 
# Get mobile devices from group
mobile_devices = response.json().get("results", [])
 
# set up variables for data collection
all_computers = []
page = 0
page_size = 100
 
print("Gathering Computer Data")
# Gather all computer data in jamf v2 inventory. Necessary due to the v2 inventory being the only place the managementId is stored
while True:
    response = requests.get(f"{JAMF}/api/v2/mobile-devices?page={page}&page-size={page_size}", headers=headers)
    data = response.json()
    computers_data = data.get("results", [])
    page += 1
 
    if not computers_data:
        break
 
    all_computers.extend(computers_data)
 
# list for storing computers restarted and failed
restarted_computers = []
pending_computers = []
failed = []
 
print("Going through data")
# loop through and restart devices
for device in mobile_devices:
    restart_pending = False
    device_id = device["mobileDeviceId"]
    print(f"Getting data for device: {device_id}")
 
    device_url = f"{JAMF}/JSSResource/mobiledevices/id/{device_id}"
    response = requests.get(device_url, headers=headers)
 
    # Grab necessary data from response
    data = response.json()
    mobile_device = data.get("mobile_device", {})
    general_info =  mobile_device.get("general", {})
 
    # Get serial number
    serial_number = general_info.get("serial_number")
 
    # Get managementId bassed off of serial number
    device_info = next((d for d in all_computers if d['serialNumber'] == serial_number), None)
 
    management_id = device_info.get("managementId")
 
    print(f"Found management id: {management_id}")
 
    # Confirm that device does not have a pending restart
    command_url = f"{JAMF}/api/v2/mdm/commands"
    params = {
        "filter": f'clientManagementId=="{management_id}" and status=="PENDING"',
        "page": 0,
        "size": 100
    }
    response = requests.get(command_url, headers=headers, params=params)
    response.raise_for_status()
 
    # Grab pending info if it exists
    pending = response.json().get("results", [])
 
    # Make sure that pending info exists
    if pending:
        # Determine if restart is one of the pending cmds
        for pending_cmd in pending:
 
            if pending_cmd.get("commandState") == 'PENDING' and pending_cmd.get("commandType") == 'RESTART_DEVICE':
                print(f"iPad {device_id} has pending restart already")
                pending_computers.append(device_info['serialNumber'])
                restart_pending = True
 
    # If no restart pending, send restart cmd to device
    if not restart_pending:
        print(f"Sending reboot cmd to device: {device_id}")
       
        # set up restart cmd url  and payload for restart
        restart_url = f"{JAMF}/api/v2/mdm/commands"
        payload = {
            "clientData": [{ "managementId": management_id }],
            "commandData": { "commandType": "RESTART_DEVICE" }
        }
 
        # send reboot cmd to device
        try:
            response = requests.post(restart_url, json=payload, headers=headers)
            response.raise_for_status()
        except:
            print(f"Failed to send restart command to {device_info['id']}, {device_info['serialNumber']}")
            failed.append({device_info['serialNumber']})
            continue
       
        # add successfully restarted computer to list
        restarted_computers.append({device_info['serialNumber']})
   
# Print out successfully rebooted computers
print(f"\nSuccessfully restarted iPads: {restarted_computers}")
 
# Print out computers with pending restart
print(f"iPads with restart cmd already pending: {pending_computers}")
 
# Check for failed computers
if (failed):
    print(f"\nThe following iPads were not restarted: {failed}")
else:
    print("\nAll iPads successfully restarted")