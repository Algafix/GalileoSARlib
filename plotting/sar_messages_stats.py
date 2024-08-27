#
# Plot statistical information about the SAR messages received:
# - SAR messages by message type (TEST_SERVICE, ACK_SERVICE...)
# - SAR messages by protocol type (Orbitography, RLS Location...)
# - RLS Location messages by beacon type (Test, PLB, EPIRB...)
# - RLS Location messages by country code
###########################################################################

import json

import numpy as np
import matplotlib.pyplot as plt

FILENAME = "./raw_data/2024-07-12.json"
FILENAME = "./raw_data/2024-08-25.json"
FILENAME = "./raw_data/2024-08-24.json"

sar_messages = {}
sar_protocols = {}
rls_beacon_types = {}
rls_by_country_code = {}

with open(FILENAME, 'r') as fd:
    all_sar_json = json.load(fd)

for sar_message in all_sar_json:

    message = sar_message['message_code']['value']
    protocol = sar_message['beacon_id_parsing_subblock']['protocol_code']['value']

    if message not in sar_messages:
        sar_messages[message] = 0
    if protocol not in sar_protocols:
        sar_protocols[protocol] = 0

    sar_messages[message] += 1
    sar_protocols[protocol] += 1

    if protocol == 'RLS Location Protocol':
        beacon_type = sar_message['beacon_id_parsing_subblock']['beacon_type']['value']
        country_code = sar_message['beacon_id_parsing_subblock']['country_code']['value']
        if beacon_type not in rls_beacon_types:
            rls_beacon_types[beacon_type] = {}
        if country_code not in rls_beacon_types[beacon_type]:
            rls_beacon_types[beacon_type][country_code] = 0
        rls_beacon_types[beacon_type][country_code] += 1

plt.figure()
plt.title(f"SAR messages received by message type")
plt.pie(sar_messages.values(), labels=sar_messages.keys(), autopct='%1.1f%%')
plt.tight_layout()

################################

plt.figure()
plt.title(f"SAR messages received by protocol type")
plt.pie(sar_protocols.values(), labels=sar_protocols.keys(), autopct='%1.1f%%')
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