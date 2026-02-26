import requests
import json
import sqlite3
from datetime import date
 
# Function for acquiring extension attribute data
def get_extension_attr(extension_attributes, name):
    # grab extension attr by name
    wanted_attr = next(
    (ea for ea in extension_attributes if ea.get("name") == name), None)
 
    # get value in exten attr
    value = wanted_attr.get("values", [])
 
    return value
 
# Function for cleaning variables
def clean(value):
    if isinstance(value, list):
        return ", ".join(map(str, value))
    elif value is None:
        return "No value recorded"
    return str(value)
 
# Create database file if it doesn't already exist and set up cursor
conn = sqlite3.connect('Power_Tracking.db')
cursor = conn.cursor()
cursor.execute('PRAGMA foreign_keys = ON')
 
# Create tables for Power Tracking db if they do not already exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS computers (
        computerId INTEGER PRIMARY KEY,
        serialNumber TEXT,
        model TEXT,
        modelIdentifier TEXT,
        computerName TEXT,
        lastCheckIn TEXT
    )
''')
conn.commit()
 
cursor.execute('''    
    CREATE TABLE IF NOT EXISTS usage (
        id INTEGER PRIMARY KEY,
        computerID INTEGER,
        date DATE,
        power TEXT,
        downtime TEXT,
        userTime TEXT,
        sleepTime TEXT,
        uptime TEXT,
        FOREIGN KEY (computerId) REFERENCES computers(computerId)
    )
''')
 
# get current date
current_date = date.today()
 
# URL for NAU Jamf Pro
JAMF_PRO_URL = ""
 
# authorization
client_id = ""
client_secret = ""
 
# set up URL and data for response
token_url = f"{JAMF_PRO_URL}/api/oauth/token"
headers = { "Content-Type": "application/x-www-form-urlencoded" }
data = f"client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
 
# Request Token from API
response = requests.post(token_url, headers=headers, data=data)
 
# If unauthorized, print details
if response.status_code != 200:
    print(f"Error {response.status_code}: {response.text}")
    response.raise_for_status()
 
# Process data returned
data = response.json()
 
api_token = data["access_token"]
 
# Print recieved token
print("API Token Acquired")
 
# Code to retrieve all computers from Jamf with General and Hardware information
computers_url = f"{JAMF_PRO_URL}/api/v1/computers-inventory?section=GENERAL&section=HARDWARE"
headers = {
    "Authorization": f"Bearer {api_token}",
    "Accept": "application/json",
}
all_computers = []
page = 0
page_size = 100
 
print("Gathering Computer Data")
# Gather all computer data in jamf inventory
while True:
    response = requests.get(f"{computers_url}&page={page}&page-size={page_size}", headers=headers)
    data = response.json()
    computers_data = data.get("results", [])
    page += 1
 
    if not computers_data:
        break
 
    all_computers.extend(computers_data)
 
print("Processing Computer Data")
# Process the retrieved computer data
for computer in all_computers:
    general_info = computer.get("general", {})
    extension_attributes = general_info.get("extensionAttributes", [])
    hardware = computer.get("hardware", {})
 
    # Get Computer ID
    computer_id = int(computer.get("id"))
 
    # Get Serial Number
    serial = hardware.get("serialNumber")
 
    # Get Model
    model = hardware.get("model")
 
    # Get Model Identifier
    model_identifier = hardware.get("modelIdentifier")
 
    # Get computer name
    computer_name = general_info.get("name")
 
    # Get last check in
    check_in = general_info.get("lastContactTime")
 
    # Get Power Usage
    power = get_extension_attr(extension_attributes, "Total Power Consumption - 24 hours")
 
    # Get Downtime
    downtime = get_extension_attr(extension_attributes, "Total Downtime - 24 hours")
 
    # Get User Time
    usage = get_extension_attr(extension_attributes, "Total Logged User Time - 24 hours")
    print(power)
    print(clean(power))
 
    # Get Sleep Time
    sleep = get_extension_attr(extension_attributes, "Total Sleep Time - 24 hours")
 
    # Get Uptime
    uptime = get_extension_attr(extension_attributes, "Total Uptime - 24 hours")
 
    # Insert computer info into computers table
    cursor.execute("INSERT OR IGNORE INTO computers (computerId, serialNumber, model, modelIdentifier, computerName, lastCheckIn) VALUES (?, ?, ?, ?, ?, ?)",
                   (computer_id, serial, model, model_identifier, computer_name, check_in))
 
    conn.commit()
 
    # Insert data into usage table
    cursor.execute(" INSERT INTO usage (computerId, date, power, downtime, userTime, sleepTime, uptime) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (computer_id, current_date, clean(power), clean(downtime), clean(usage), clean(sleep), clean(uptime)))
 
# check for data input success
if cursor:
    print("Data Successfully Insereted")
else:
    print("Data Insertion Failure")
 
# Commit changes to database
conn.commit()
 
# Number of computers screened
print(f"\nTotal Computers Screened: {len(all_computers)}")
 
# Close database connection
conn.close()
 
# Invalidate the API token once operations complete for security
invalidate_token_url = f"{JAMF_PRO_URL}/api/v1/auth/invalidate-token"
headers = {
    "Authorization": f"Bearer {api_token}",
}
 
response = requests.post(invalidate_token_url, headers=headers)
response.raise_for_status()
print("\nAPI token invalidated successfully.")