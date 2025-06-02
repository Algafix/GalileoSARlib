import sys
sys.path.insert(0, '.')

import json

import numpy as np
import matplotlib.pyplot as plt

from bitstring import BitArray

FILENAME = "./ENC25_DATA/ENC25_unknown_protocols.json"

undefined_rls_dict = {
    "SHORT_RLM": {
        "msg_dates": {},
        "msg_beacons": set(),
        "msg_codes": set()
    },
    "LONG_RLM": {
        "msg_dates": {},
        "msg_beacons": set(),
        "msg_codes": set()
    }
}

with open(FILENAME, 'r') as fd:
    all_long_json = json.load(fd)

for sar_message in all_long_json:

    rlm_dict =  undefined_rls_dict[sar_message["rlm_id"]["value"]]

    beacon_id = sar_message["beacon_id"]["raw_value"]
    rlm_dict["msg_beacons"].add(beacon_id)

    msg_code = sar_message["message_code"]["raw_value"]
    rlm_dict["msg_codes"].add(msg_code)

    date = sar_message["metadata"]["utc"].split()[0]
    if date not in rlm_dict["msg_dates"]:
        rlm_dict["msg_dates"][date] = 1
    else:
        rlm_dict["msg_dates"][date] += 1

print(undefined_rls_dict)
print(sum([v for v in undefined_rls_dict["SHORT_RLM"]["msg_dates"].values()]))
print(sum([v for v in undefined_rls_dict["LONG_RLM"]["msg_dates"].values()]))



