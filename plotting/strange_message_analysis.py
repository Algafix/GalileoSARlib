import sys
sys.path.insert(0, '.')

import json

import numpy as np
import matplotlib.pyplot as plt

from bitstring import BitArray
from aux.protocol_parsing import convert_baudot

FILENAME = "./ENC25_DATA/ENC25_sar_3_months.json"

msg_beaconid = {}
msg_tows = []
msg_code = {"Test Service": [], "Ack Service": [], 'Spare': []}

with open(FILENAME, 'r') as fd:
    all_sar_json = json.load(fd)


for sar_message in all_sar_json:
    if sar_message['beacon_id']['raw_value'][:5] == 'aaaaa':

        msg_tows.append(sar_message["metadata"]["tow"])

        if sar_message["message_code"]["value"] == "TEST_SERVICE":
            msg_code['Test Service'].append(sar_message)
        elif sar_message["message_code"]["value"] == "ACK_SERVICE":
            msg_code['Ack Service'].append(sar_message)
        else:
            msg_code['Spare'].append(sar_message)

        beacon_id = sar_message['beacon_id']['raw_value']
        try:
            msg_beaconid[beacon_id] += 1
        except KeyError:
            msg_beaconid[beacon_id] = 1

        if 'ffffffff' in beacon_id:
            print(f"{sar_message['metadata']['utc']} - {beacon_id} - {BitArray(bin=sar_message['rlm_params']['raw_value']).hex}")

translated_names = []
for beaconid in msg_beaconid:
    translated_names.append(convert_baudot(BitArray(hex=beaconid[5:])[:-4]))

print(msg_beaconid)

print(translated_names)
print({k:len(v) for k,v in msg_code.items()})

for msg in msg_code["Ack Service"]:
    print(f"{msg['metadata']['utc']} - {msg['beacon_id']['raw_value']} - {BitArray(bin=msg['rlm_params']['raw_value']).hex}")





