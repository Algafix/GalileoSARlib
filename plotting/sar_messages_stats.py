#
# Plot statistical information about the SAR messages received:
# - SAR messages by message type (TEST_SERVICE, ACK_SERVICE...)
# - SAR messages by protocol type (Orbitography, RLS Location...)
# - RLS Location messages by beacon type (Test, PLB, EPIRB...)
# - RLS Location messages by country code
###########################################################################
import sys
sys.path.insert(0, '.')

import json

import numpy as np
import matplotlib.pyplot as plt

from bitstring import BitArray
from aux.protocol_parsing import convert_baudot

FILENAME = "./raw_data/2024-07-12.json"
FILENAME = "./raw_data/2024-08-25.json"
FILENAME = "./raw_data/2024-08-24.json"
FILENAME = "./raw_data/2024-11-17.json"

sar_messages = {}
sar_protocols = {}
sar_by_message_code = {}
rls_beacon_types = {}
rls_by_country_code = {}
strange_messages = {}

with open(FILENAME, 'r') as fd:
    all_sar_json = json.load(fd)

################################
# Create a dictionary by message type and another by protocol

for sar_message in all_sar_json:

    # Some strange test messages, skip further processing if thats the case
    if sar_message['beacon_id']['raw_value'][:5] == 'aaaaa':
        beacon_id = sar_message['beacon_id']['raw_value']
        msg = convert_baudot(BitArray(hex=beacon_id[5:])[:-4])
        try:
            strange_messages[msg] += 1
        except KeyError:
            strange_messages[msg] = 0
        continue


    message_code = sar_message['message_code']['value']
    protocol = sar_message['beacon_id_parsing_subblock']['protocol_code']['value']

    if message_code not in sar_messages:
        sar_messages[message_code] = 0
    if protocol not in sar_protocols:
        sar_protocols[protocol] = 0
    if message_code not in sar_by_message_code:
        sar_by_message_code[message_code] = []

    sar_messages[message_code] += 1
    sar_protocols[protocol] += 1
    sar_by_message_code[message_code].append(sar_message)

    if protocol == 'RLS Location Protocol':
        beacon_type = sar_message['beacon_id_parsing_subblock']['beacon_type']['value']
        country_code = sar_message['beacon_id_parsing_subblock']['country_code']['value']
        if beacon_type not in rls_beacon_types:
            rls_beacon_types[beacon_type] = {}
        if country_code not in rls_beacon_types[beacon_type]:
            rls_beacon_types[beacon_type][country_code] = 0
        rls_beacon_types[beacon_type][country_code] += 1

################################
# Get protocols for TEST and ACK message types

def extract_protocols(message_code, sar_by_message_code):
    protocols_count = {}
    for sar_message in sar_by_message_code[message_code]:
        protocol = sar_message['beacon_id_parsing_subblock']['protocol_code']['value']
        try:
            protocols_count[protocol] += 1
        except KeyError:
            protocols_count[protocol] = 0
    return protocols_count

test_protocols = extract_protocols("TEST_SERVICE", sar_by_message_code)
ack_protocols = extract_protocols("ACK_SERVICE", sar_by_message_code)

fig, axs = plt.subplots(3, 1, figsize=(5,9))
fig.suptitle(f"SAR messages received by message type")
axs[0].pie(sar_messages.values(), labels=sar_messages.keys(), autopct='%1.1f%%')
axs[0].set_title('by service')
axs[1].pie(test_protocols.values(), labels=test_protocols.keys(), autopct='%1.1f%%')
axs[1].set_title('Protocols in TEST SERVICE')
axs[2].pie(ack_protocols.values(), labels=ack_protocols.keys(), autopct='%1.1f%%')
axs[2].set_title('Protocols in ACK SERVICE')
plt.tight_layout()

################################

plt.figure()
plt.title(f"SAR messages received by protocol type")
plt.pie(sar_protocols.values(), labels=sar_protocols.keys(), autopct='%1.1f%%')
plt.tight_layout()

################################

plt.figure()
plt.title(f"Strange messages with Beacon ID starting with: AAAAA")
plt.bar(strange_messages.keys(), strange_messages.values())
plt.tight_layout()

################################

plt.figure()
plt.title(f"RLS Location Protocol messages received by beacon type")
plt.pie(
    [sum(countries.values()) for countries in rls_beacon_types.values()], 
    labels=rls_beacon_types.keys(), 
    autopct='%1.1f%%'
)
plt.tight_layout()

################################

plt.figure()
plt.title(f"RLS Location Protocol messages received by beacon type and country")

cmap = plt.colormaps["tab20c"]  # 4 variation per colour
outer_colors = cmap([1,4,8])
inner_colors = cmap([2,5,9,10,11])
size = 0.3

plt.pie(
    [sum(countries.values()) for countries in rls_beacon_types.values()],
    labels=rls_beacon_types.keys(), 
    colors=outer_colors,
    radius=1,
    autopct='%1.1f%%',
    pctdistance=0.85,
    wedgeprops=dict(width=size, edgecolor='w')
)

plt.pie(
    [value for countries in rls_beacon_types.values() for value in countries.values()],
    labels=[country for countries in rls_beacon_types.values() for country in countries.keys()],
    colors=inner_colors,
    radius=1-size,
    wedgeprops=dict(width=size, edgecolor='w'),
    labeldistance=0.2,
    rotatelabels=True,
)
plt.tight_layout()

plt.show()