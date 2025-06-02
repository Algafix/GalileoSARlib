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


FILENAME = "./raw_data/sept100.json"
#FILENAME = "./SAR_DATA/ENC25_sar_3_months.json"

sar_messages = {}
sar_protocols = {}
sar_by_message_code = {}
strange_messages = {}
rlm_types = {'SHORT': {}, 'LONG': {}}

with open(FILENAME, 'r') as fd:
    all_sar_json = json.load(fd)

################################
# Create a dictionary by message type and another by protocol

for sar_message in all_sar_json:

    # Some strange test messages, skip further processing if thats the case
    if sar_message['message_code']['value'] != 'SPARE' and sar_message['rlm_id']['value'] == "SHORT_RLM" and sar_message['beacon_id']['raw_value'][:5] == 'aaaaa':
        beacon_id = sar_message['beacon_id']['raw_value']
        msg = convert_baudot(BitArray(hex=beacon_id[5:])[:-4])
        try:
            strange_messages[msg] += 1
        except KeyError:
            strange_messages[msg] = 1
        continue
    ####################

    if sar_message['rlm_id']['value'] == "SHORT_RLM":
        rlm_type = rlm_types['SHORT']
    else:
        rlm_type = rlm_types['LONG']
    message_code = sar_message['message_code']['value']
    try:
        rlm_type[message_code] += 1
    except KeyError:
        rlm_type[message_code] = 1

    ####################

    if message_code not in sar_messages:
        sar_messages[message_code] = 0
    if message_code not in sar_by_message_code:
        sar_by_message_code[message_code] = []
    sar_messages[message_code] += 1
    sar_by_message_code[message_code].append(sar_message)

    ####################

    if message_code == "SPARE":
        continue

    protocol = sar_message['beacon_id_parsing_subblock']['protocol_code']['value']

    if protocol not in sar_protocols:
        sar_protocols[protocol] = 0
    sar_protocols[protocol] += 1

################################
# Get percentage for SHORT and LONG RLM

print(rlm_types)

fig, axs = plt.subplots(1, 2, figsize=(9,5))
fig.suptitle(f"RLM received in 90 days")
axs[0].pie([sum(rlm_type.values()) for rlm_type in rlm_types.values()], labels=rlm_types.keys(), autopct='%1.1f%%', textprops={'fontsize': 12})
axs[0].set_title('by RLM type')
axs[1].pie(sar_messages.values(), labels=sar_messages.keys(), autopct='%1.1f%%', textprops={'fontsize': 12})
axs[1].set_title('by RLS type')
plt.tight_layout()

plt.figure()
plt.title(f"RLM Types")
cmap = plt.colormaps["tab20c"]  # 4 variation per colour
outer_colors = cmap([1,4,8])
inner_colors = cmap([2,5,9,10,11])
size = 0.3
plt.pie(
    [sum(rlm_type.values()) for rlm_type in rlm_types.values()],
    labels=rlm_types.keys(),
    colors=outer_colors,
    radius=1,
    autopct='%1.1f%%',
    pctdistance=0.85,
    wedgeprops=dict(width=size, edgecolor='w')
)
plt.pie(
    [count for rlm_type in rlm_types.values() for count in rlm_type.values()],
    labels=[name for rlm_type in rlm_types.values() for name in rlm_type.keys()],
    colors=inner_colors,
    radius=1-size,
    autopct='%1.1f%%',
    wedgeprops=dict(width=size, edgecolor='w'),
    labeldistance=0.2,
    pctdistance=0.85,
    rotatelabels=True,
)
plt.tight_layout()


################################
# Get protocols for TEST and ACK service types

def extract_protocols(message_code, sar_by_message_code):
    protocols_count = {}
    for sar_message in sar_by_message_code[message_code]:
        protocol = sar_message['beacon_id_parsing_subblock']['protocol_code']['value']
        try:
            protocols_count[protocol] += 1
        except KeyError:
            protocols_count[protocol] = 1
    return protocols_count

test_protocols = extract_protocols("TEST_SERVICE", sar_by_message_code)
ack_protocols = extract_protocols("ACK_SERVICE", sar_by_message_code)

print(test_protocols)
print(ack_protocols)

fig, axs = plt.subplots(1, 2, figsize=(9,5))
fig.suptitle(f"SAR messages received by message type")
axs[0].pie(test_protocols.values(), labels=test_protocols.keys(), autopct='%1.1f%%')
axs[0].set_title('Protocols in TEST SERVICE')
axs[1].pie(ack_protocols.values(), labels=ack_protocols.keys(), autopct='%1.1f%%')
axs[1].set_title('Protocols in ACK SERVICE')
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

plt.show()