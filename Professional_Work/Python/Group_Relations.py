import requests
import threading
import time
 
# If you would like to see full verbose printing, go through and remove comments on print statements in code
 
JAMF = ""
groups_list = []
counter = 0
 
# Lock to pause main code while refreshing token
token_lock = threading.Lock()
access_token = None
headers = {}
 
# Group class to handle collection of relational data
class Group:
    def __init__(self, name, id, smart_group, policies_data=None, group_data=None, configuration_data=None):
        self.name = name
        self.id = id
        self.smart_group = smart_group
        if policies_data is None:
            self.policies_set = set()
        else:
            self.policies_set = set(policies_data)
       
        if group_data is None:
            self.groups_set = set()
        else:
            self.groups_set = set(group_data)
 
        if configuration_data is None:
            self.configurations_set = set()
        else:
            self.configurations_set = set(configuration_data)
 
    def add_policy(self, policy):
        self.policies_set.add(policy)
 
    def get_policies(self):
        return list(self.policies_set)
   
    def add_group(self, group):
        self.groups_set.add(group)
 
    def get_groups(self):
        return list(self.groups_set)
   
    def add_configuration(self, configuration):
        self.configurations_set.add(configuration)
   
    def get_configurations(self):
        return list(self.configurations_set)
 
# Function for grabbing access token
def getAccessToken():
    # Fetch a new Jamf API token and update global headers.
    global access_token, headers
    client_secret = {
        "client_name": "",
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
print("\nStarting Computer Groups Relation Script\nThis script will take multiple minutes to run and there will be some time between update print outs\n" \
"The final information print out will be in the form of smart groups followed by static groups\n")
 
# Start background token refresher
threading.Thread(target=refresh_token_periodically, daemon=True).start()
 
# get access token
getAccessToken()
 
# Get All Computer Groups in Jamf
response = safe_get(f"{JAMF}/api/v1/computer-groups")
groups = response.json()
 
print("Generating Groups and related smart groups")
# Go through each group and create Group Objects
for group in groups:
    # Get Group Info
    id = int(group.get("id"))
    name = group.get("name")
    smart_group = group.get("smartGroup")
    #print(f"ID: {id}, Name: {name}, Smart Group: {smart_group}")
 
    # Create group object and append to groups_list
    new_group = Group(name, id, smart_group)
 
    if smart_group:
        # Grab criteria info
        response = safe_get(f"{JAMF}/api/v2/computer-groups/smart-groups/{group.get("id")}")
 
        data = response.json()
        criteria = data.get("criteria")
 
        # Loop through each criteria and add it to the new_group
        for item in criteria:
            if item.get("name") == "Computer Group":
                new_group.add_group(item.get("value"))
 
    groups_list.append(new_group)
    counter += 1
    # print(f"Group: {new_group.name} successfully added to list with group_set: {new_group.groups_set}")
 
print("Determining related configuration profiles")
# Grab all Configuration Profiles
response = safe_get(f"{JAMF}/JSSResource/osxconfigurationprofiles")
data = response.json()
profiles = data.get("os_x_configuration_profiles", {})
 
# Go through each Configuration Profile to determine Scope
for profile in profiles:
    id = profile.get("id")
    name = profile.get("name")
    #print(f"\nInfo for Configuration Profile: {name}; ID: {id}")
 
    # Get scope of Configuration profile
    response = safe_get(f"{JAMF}/JSSResource/osxconfigurationprofiles/id/{id}/subset/Scope")
    data = response.json()
 
    # Determine Computer Groups in scope
    configuration = data.get("os_x_configuration_profile", {})
    scope = configuration.get("scope")
    computer_groups = scope.get("computer_groups")
 
    # If Computer Groups, add to group
    if computer_groups:
        # go through each computer group and add configuration profile to group cofniguration set
        for group in computer_groups:
            id = group.get("id")
            # check for id in group objects
            for current_group in groups_list:
                # if id matches, add configuration profile name to group
                if current_group.id == id:
                    #print(f"Adding configuration profile: {name} to group {current_group.name}")
                    current_group.add_configuration(name)
                    break
 
print("Determining related policies")
# Get All Jamf Policies
response = safe_get(f"{JAMF}/JSSResource/policies")
policies = response.json().get("policies", [])
 
# Loop through each policy to determine groups in scope
for policy in policies:
 
    id = policy.get("id")
    name = policy.get("name")
    # use id to get detailed policy info
    response = safe_get(f"{JAMF}/JSSResource/policies/id/{id}/subset/Scope")
 
    # Get json policy data out of response
    policy_details = response.json()
    policy_data = policy_details.get("policy", {})
 
    # Display name & id of policy being checked
    #print(f"\nInfo for Policy: {name}; ID: {id}")
 
    # Get groups that policy is scoped out to
    scope = policy_data.get("scope", {}) # check for all computers true to maybe add count for that
    computer_groups = scope.get("computer_groups", [])
 
    if computer_groups:
        # go through each computer group and add policy to group policy set
        for group in computer_groups:
            id = group.get("id")
            # check for id in group objects
            for current_group in groups_list:
                # if id matches, add policy name to group
                if current_group.id == id:
                    #print(f"Adding policy: {name} to group {current_group.name}")
                    current_group.add_policy(name)
                    break
 
# Display Groups with policies associated with them
print("Writing information to Computer Group Relations.txt within current directory")
 
# write relational information to file
with open("Computer Group Relations.txt", "w", encoding="utf-8") as file:
    # Display Groups with policies associated with them
    file.write("### SMART GROUPS ###")
    for group in groups_list:
        # Check if Smart Group:
        if group.smart_group:
            file.write(f"\nGroup: {group.name}\n  Configuration Profiles: {group.get_configurations()}\n  Policies: {group.get_policies()}\n  and Groups: {group.get_groups()}")
            file.write("\n")
 
    file.write("\n\n### STATIC GROUPS ###")
    for group in groups_list:
        if group.smart_group:
            continue
        else:
            file.write(f"\nGroup: {group.name}\n  Configuration Profiles: {group.get_configurations()}\n  Policies: {group.get_policies()}\n  and Groups: {group.get_groups()}")
            file.write("\n")