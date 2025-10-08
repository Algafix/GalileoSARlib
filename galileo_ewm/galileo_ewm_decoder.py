import sys
sys.path.insert(0, '.')

import json
import numpy as np
import matplotlib.pyplot as plt

from bitstring import BitArray

from EWM import EWM

FILENAME = "raw_data/galileo_ewm_long.json"

with open(FILENAME, 'r') as fd:
    all_long_json = json.load(fd)

ewm_candidates = []
ewm_wn = []

for sar_message in all_long_json:

    if sar_message['rlm_id']['value'] != "LONG_RLM":
        continue

    full_160bits = BitArray(hex=sar_message["beacon_id"]["raw_value"]) + BitArray(bin=sar_message["message_code"]["raw_value"]) + BitArray(bin=sar_message["rlm_params"]["raw_value"])

    # First 21 bits equal to 0
    # next 122 have message
    # last 17 bits idk

    if full_160bits.bin[:21] != '0'*21:
        continue

    ewm_candidate = full_160bits[21:]
    
    if ewm_candidate not in ewm_candidates:
        ewm_candidates.append(ewm_candidate)
        ewm_wn.append(sar_message['metadata']['wn'])

for ewm, wn in zip(ewm_candidates, ewm_wn):
    ewm_object = EWM(ewm.bin, wn)
    print(ewm_object)


# 0000000000000000000000101101000000001100010011000001000101010101100000000001000101011101110110101100000011101000010110001011001000000000000010110000000000000000
# 0000000000000000000001101101000000001100010011000001000101010101100000000001000101011101110110101100000011101000010110001011001000000000000010110000000000000001

