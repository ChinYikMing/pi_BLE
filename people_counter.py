#!/usr/bin/env python

from bluetooth.ble import BeaconService
import argparse
import sys
import subprocess
import time
from os.path import exists

class Beacon:
    def __init__(self, data, address):
        self.uuid = data[0]
        self.major = data[1]
        self.minor = data[2]
        self.power = data[3]
        self.rssi = data[4]
        self.address = address
        self.reward = 0

    def __str__(self):
        ret = "Beacon: address:{ADDR} uuid:{UUID} major:{MAJOR} " \
              "minor:{MINOR} txpower:{POWER} rssi:{RSSI}" \
              .format(ADDR=self.address, UUID=self.uuid, MAJOR=self.major,
                      MINOR=self.minor, POWER=self.power, RSSI=self.rssi)
        return ret

service = BeaconService()

application_name = "beacon_scanner"
url = "https://rog.asus.com"

schemes = [
        "http://www.",
        "https://www.",
        "http://",
        "https://",
        ]

extensions = [
        ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
        ".com", ".org", ".edu", ".net", ".info", ".biz", ".gov",
        ]

if (sys.version_info > (3, 0)):
    DEVNULL = subprocess.DEVNULL
else:
    DEVNULL = open(os.devnull, "wb")

# parser = argparse.ArgumentParser(prog=application_name, description=__doc__)
# parser.add_argument('-t', '--nrScan', type=int, default=10, help='number of scanning')
# parser.add_argument('-f', '--RSSIFilename', type=str, default=None, help='RSSI filename to store RSSI data')
# args = parser.parse_args()

# if args.RSSIFilename == None:
#     print("Please give a filename for storing RSSI data")
#     parser.print_help()
#     exit()

# nr_scan = args.nrScan
# RSSI_filename = args.RSSIFilename + ".log"
people_counter_file = "people_counter"

def encodeurl(url):
    i = 0
    data = []

    for s in range(len(schemes)):
        scheme = schemes[s]
        if url.startswith(scheme):
            data.append(s)
            i += len(scheme)
            break
    else:
        raise Exception("Invalid url scheme")

    while i < len(url):
        if url[i] == '.':
            for e in range(len(extensions)):
                expansion = extensions[e]
                if url.startswith(expansion, i):
                    data.append(e)
                    i += len(expansion)
                    break
            else:
                data.append(0x2E)
                i += 1
        else:
            data.append(ord(url[i]))
            i += 1

    return data


def encodeMessage(url):
    encodedurl = encodeurl(url)
    encodedurlLength = len(encodedurl)

    print("Encoded url length: " + str(encodedurlLength))

    if encodedurlLength > 18:
        raise Exception("Encoded url too long (max 18 bytes)")

    message = [
            0x02,   # Flags length
            0x01,   # Flags data type value
            0x1a,   # Flags data

            0x03,   # Service UUID length
            0x03,   # Service UUID data type value
            0xaa,   # 16-bit Eddystone UUID
            0xfe,   # 16-bit Eddystone UUID

            5 + len(encodedurl), # Service Data length
            0x16,   # Service Data data type value
            0xaa,   # 16-bit Eddystone UUID
            0xfe,   # 16-bit Eddystone UUID

            0x10,   # Eddystone-url frame type
            0xed,   # txpower
            ]

    message += encodedurl

    return message


def advertise(url):
    print("Advertising: " + url)
    message = encodeMessage(url)

    # Prepend the length of the whole message
    message.insert(0, len(message))

    # Pad message to 32 bytes for hcitool
    while len(message) < 32: message.append(0x00)

    # Make a list of hex strings from the list of numbers
    message = map(lambda x: "%02x" % x, message)

    # Concatenate all the hex strings, separated by spaces
    message = " ".join(message)
    print("Message: " + message)

    subprocess.call("sudo hciconfig hci0 up", shell = True, stdout = DEVNULL)

    # Stop advertising
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000a 00", shell = True, stdout = DEVNULL)

    # Set message
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 " + message, shell = True, stdout = DEVNULL)

    # Resume advertising
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000a 01", shell = True, stdout = DEVNULL)

def match_beacon(uuid):
    for key in beacons.keys():
        if key == uuid:
            return True
    return False

# main logic
# RSSI_file = open(RSSI_filename, "w+")
e_counter = 0
RSSI_acc = 0
rcv_counter = 0
found = True

beacons = []

# UUID
# 6cdf66a2-0573-4f16-ab00-7f784ea85f69
# 0a2cae6a-e640-46f7-a86a-da3e583b7be8
# 6249a871-036c-436c-8024-9d45709ddb65

while True:
    devices = service.scan(1)
    counter_file = open(people_counter_file, "w")
    # print(list(devices.items()))
    if list(devices.items()) == []:
        # print("clear")
        beacons.clear()
    else :
        for i, (addr, data) in enumerate(list(devices.items())):
            beacon = Beacon(data, addr)

            # Find whether same uuid exist or not
            found = False
            for b in beacons:
                if b.uuid == beacon.uuid:
                    b.rssi = beacon.rssi
                    # If RSSI is bigger than a threshold, reward increase
                    if int(b.rssi) >= -60:
                        if b.reward < 3:
                            b.reward += 1
                        # advertise the ads if reward equal to 3
                        if b.reward == 3:
                            pass
                            # TODO:  It leads to advertise too many times.
                            advertise(url)
                    else:
                        b.reward = 0
                    found = True
            # If uuid doesn't exist, then add beacon's information into list
            if not found:
                beacons.append(beacon)
        
    # count number of people
    num_people = 0
    for i in beacons:
        if i.reward == 3:
            num_people += 1
    #print("nuber of people: " + str(num_people))
    counter_file.write(str(num_people) + "\n")
