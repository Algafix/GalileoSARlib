import json

import numpy as np
import matplotlib.pyplot as plt


FILENAME = "./raw_data/2024-07-12.json"

with open(FILENAME, 'r') as fd:
    all_sar_json = json.load(fd)

rls_by_beacon_type = {}

for sar_message in all_sar_json:

    if sar_message['beacon_id_parsing_subblock']['protocol_code']['value'] == 'RLS Location Protocol':

        svid = int(sar_message['metadata']['svid'])
        tow = sar_message['metadata']['tow']
        message_type = sar_message['message_code']['value']
        beacon_type = sar_message["beacon_id_parsing_subblock"]["beacon_type"]['value']

        if beacon_type not in rls_by_beacon_type:
            rls_by_beacon_type[beacon_type] = {'svid':[], 'tow':[]}
        
        rls_by_beacon_type[beacon_type]['svid'].append(svid)
        rls_by_beacon_type[beacon_type]['tow'].append(tow)

for protocol, messages in rls_by_beacon_type.items():
    plt.figure()
    plt.title(f"{protocol} - Reception time offset within 2 subframes period")
    plt.xlabel("Seconds in GNSS Time")
    plt.ylabel("Number of messages")
    tows_mod_60_sec = [tow % 60 for tow in messages["tow"]]
    unique_tows, counts = np.unique(tows_mod_60_sec, return_counts=True)
    str_unique_tows = [str(unique_tow) for unique_tow in unique_tows]
    plt.bar(str_unique_tows, counts)

plt.show()
        


