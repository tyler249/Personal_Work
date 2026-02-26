import sqlite3
import csv
from datetime import date
 
# Formatting for power usage
def format_value(value, decimals=2):
    if value is None:
        return ""
    try:
        # Try to format as float
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        # If not numeric, return as string
        return str(value)
 
# Setup connectiond
conn = sqlite3.connect('Power_Tracking.db')
cursor = conn.cursor()
cursor.execute('PRAGMA foreign_keys = ON')
 
# get current date
current_date = date.today()
 
# grab all computer ids in database
cursor.execute("SELECT computerId FROM computers")
computers = cursor.fetchall()
 
# Open CSV file for writing
with open(f'{current_date}.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = [
        "Computer Id", "Serial Number", "Model", "Model Identifier", "Computer Name",
        "Last Check In", "Power Usage (kwh)", "Downtime", "User Usage", "Sleep Time", "Uptime"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
 
    # loop through every computer id to grab usage info
    for (computer_id,) in computers:
 
        # Get computer info
        cursor.execute('SELECT * FROM computers WHERE computerId = ?', (computer_id,))
        computer = cursor.fetchone()
 
        # Get current usage log for that computer
        cursor.execute('SELECT power, downtime, userTime, sleepTime, uptime FROM usage WHERE computerId = ? AND date = ?', (computer_id, current_date))
        usage = cursor.fetchone()
        print(usage[0])
 
        # Write row to CSV
        writer.writerow({
            "Computer Id": computer[0],
            "Serial Number": computer[1],
            "Model": computer[2],
            "Model Identifier": computer[3],
            "Computer Name": computer[4],
            "Last Check In": computer[5],
            "Power Usage (kwh)": format_value(usage[0], 10) if usage else "",
            "Downtime": usage[1],
            "User Usage": usage[2],
            "Sleep Time": usage[3],
            "Uptime": usage[4]
        })
 
print(f"CSV file '{current_date}.csv' created successfully.")
 
conn.close()