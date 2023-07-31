import requests
import subprocess
import os
import sys

# Country code, e.g. 'us', 'cn', 'ru', 'in'
COUNTRY_CODE = 'your_country'

# File that will contain blocked IPs
BLOCKLIST_PATH = '/etc/blocklist.txt'

# Get the IP list
def get_ip_list(country_code):
    url = f'https://api.ipverse.net/api/ipcountry?country={country_code}'
    response = requests.get(url)
    return response.text

# Block IP list
def block_ip_list():
    # Make sure we are running as root
    if os.geteuid() != 0:
        print("This script must be run as root!")
        sys.exit(1)

    # Get the IP list
    ip_list = get_ip_list(COUNTRY_CODE)
    
    # Write the IPs to the blocklist file
    with open(BLOCKLIST_PATH, 'w') as f:
        f.write(ip_list)

    # Add the blocklist to the pf table
    subprocess.run(['pfctl', '-t', 'blocklist', '-T', 'replace', '-f', BLOCKLIST_PATH])

    # Enable the pf firewall if not already enabled
    if subprocess.run(['pfctl', '-s', 'info']).returncode != 0:
        subprocess.run(['pfctl', '-e'])

    # Add the block rule if it doesn't already exist
    block_rule = f'block in quick from <blocklist>'
    if block_rule not in subprocess.run(['pfctl', '-s', 'rules'], capture_output=True, text=True).stdout:
        subprocess.run(['pfctl', '-a', 'blocklist', '-f', '-', input=block_rule, text=True])

# Unblock IP list
def unblock_ip_list():
    # Make sure we are running as root
    if os.geteuid() != 0:
        print("This script must be run as root!")
        sys.exit(1)

    # Remove the block rule
    subprocess.run(['pfctl', '-a', 'blocklist', '-F', 'rules'])

    # Remove the blocklist from the pf table
    subprocess.run(['pfctl', '-t', 'blocklist', '-T', 'flush'])

# Example usage
block_ip_list()
# unblock_ip_list()
