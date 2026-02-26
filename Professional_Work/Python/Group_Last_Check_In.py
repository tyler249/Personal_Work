import requests
import threading
import time
 
JAMF = ""
groups_list = []
counter = 0
 
# Lock to pause main code while refreshing token
token_lock = threading.Lock()
access_token = None
headers = {}
 
class Group:
    def __init__(self, name):
        self.name = name
        self.computers_list = []
 
    def add_computer(self, computer):
        self.computers_list.append(computer)
 
# Computer class to handle collection of computer data
class Computer:
    def __init__(self, name, id, serial, last_checkIn, last_inventory_update):
        self.name = name
        self.id = id
        self.serial = serial
        self.last_checkIn = last_checkIn
        self.last_inventory_update = last_inventory_update
        self.membership_list = []
 
    def add_membership(self, group):
        self.membership_list.append(group)
 
# Function for grabbing access token
def getAccessToken():
    """Fetch a new Jamf API token and update global headers."""
    global access_token, headers
    client_secret = {
        "client_name": "Group Audit and Review",
        "client_id":"",
        "client_secret":"",
        "grant_type": "client_credentials",
    }
 
    response = requests.post(f'{JAMF}/api/v2/oauth/token', data=client_secret)
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        print("[INFO] Access token refreshed")
    else:
        print("[ERROR] Unable to generate authentication token")
        exit()
 
# Background thread that refreshes the token every 2.5 minutes.
def refresh_token_periodically():
    while True:
        time.sleep(150)
        token_lock.acquire()
        try:
            getAccessToken()
        finally:
            token_lock.release()
 
# Thread-safe request wrappers
def safe_get(url):
    token_lock.acquire()
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    finally:
        token_lock.release()
 
def safe_post(url, data):
    token_lock.acquire()
    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response
    finally:
        token_lock.release()
 
# START OF SCRIPT
# Start background token refresher
threading.Thread(target=refresh_token_periodically, daemon=True).start()
 
# get access token
getAccessToken()
 
print("Gathering Computer Data")
# Gather all computer data in jamf inventory
all_computers = []
page = 0
page_size = 100
computers_url = f"{JAMF}/api/v1/computers-inventory?section=GENERAL&section=HARDWARE&section=GROUP_MEMBERSHIPS"
while True:
    response = safe_get(f"{computers_url}&page={page}&page-size={page_size}")
    data = response.json()
    computers_data = data.get("results", [])
    page += 1
 
    if not computers_data:
        break
 
    all_computers.extend(computers_data)
 
print("Processing Computer Data")
# Make objects for all computers
computers = []
for computer in all_computers:
    computer_id = computer.get("id")
    general = computer.get("general")
    hardware = computer.get("hardware")
    memberships = computer.get("groupMemberships")
 
    # get computer information
    serial = hardware.get("serialNumber")
    computer_name = general.get('name')
    last_checkIn = general.get('lastContactTime')
    last_inventory_update = general.get('reportDate')
    new_computer = Computer(computer_name, computer_id, serial, last_checkIn, last_inventory_update)
 
    # look at groups that the computer is a part of
    for group in memberships:
        smart = group.get("smartGroup")
       
        # check for smart group
        if smart:
            group_id = group.get("groupId")
            new_computer.add_membership(group_id)
 
    computers.append(new_computer)
    #print(f"\nComputer Name: {computer_name}, Id: {computer_id} added to computers list")
 
print("Determining groups")
# Get All Jamf Groups
response = safe_get(f"{JAMF}/api/v1/computer-groups")
groups = response.json()
 
smart_groups = []
# Loop through each group to determine membership in scope
for group in groups:
 
    id = group.get("id")
    name = group.get("name")
    smart_group = group.get("smartGroup")
 
    if smart_group:
       
        new_group = Group(name)
 
        # Check which computers are members of the current group
        for computer in computers:
           
            # Looks for group id in membership list
            for group_id in computer.membership_list:
               
                # Print out computer info if so
                if int(group_id) == int(id):
                    new_group.add_computer(computer)
                    #print(f"\n  Name: {computer.name}, Id: {computer_id}, Serial: {computer.serial}\n  Last Check In: {computer.last_checkIn}, Last Inventory Update: {computer.last_inventory_update}")
                    break
 
        # append smart group to list
        smart_groups.append(new_group)
 
# Go through and write information to text file
with open("Group_Computer_Check-in.txt", "w", encoding="utf-8") as file:
   
    # Display Groups with computers associated with them
    for group in smart_groups:
       
        file.write(f"Smart Group: {group.name}\n")
 
        if group.computers_list:
 
            for computer in group.computers_list:
                file.write(f"   Name: {computer.name}, Id: {computer.id}, Serial: {computer.serial}\n   Last Check In: {computer.last_checkIn}, Last Inventory Update: {computer.last_inventory_update}\n\n")
 
        else:
            file.write("No computers in group\n\n")