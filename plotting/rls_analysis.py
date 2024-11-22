import json

import numpy as np
import matplotlib.pyplot as plt


FILENAME = "./raw_data/2024-07-12.json"
FILENAME = "./raw_data/2024-08-25.json"
FILENAME = "./raw_data/2024-08-24.json"
FILENAME = "./raw_data/2024-11-17.json"

with open(FILENAME, 'r') as fd:
    all_sar_json = json.load(fd)

rls_by_beacon_type = {}
rls_by_beaconID = {}

for sar_message in all_sar_json:

    if sar_message['beacon_id_parsing_subblock']['protocol_code']['value'] == 'RLS Location Protocol':

        svid = int(sar_message['metadata']['svid'])
        tow = sar_message['metadata']['tow']
        message_type = sar_message['message_code']['value']
        beaconID = sar_message['beacon_id']['raw_value']
        beacon_type = sar_message["beacon_id_parsing_subblock"]["beacon_type"]['value']

        if beacon_type not in rls_by_beacon_type:
            rls_by_beacon_type[beacon_type] = {'svid':[], 'tow':[]}
        
        if beaconID not in rls_by_beaconID:
            rls_by_beaconID[beaconID] = {'svid':[], 'tow':[]}

        rls_by_beacon_type[beacon_type]['svid'].append(svid)
        rls_by_beacon_type[beacon_type]['tow'].append(tow)
        rls_by_beaconID[beaconID]['svid'].append(svid)
        rls_by_beaconID[beaconID]['tow'].append(tow)

for protocol, messages in rls_by_beacon_type.items():
    plt.figure()
    plt.title(f"{protocol} - Reception time offset within 2 subframes period")
    plt.xlabel("Seconds in GNSS Time")
    plt.ylabel("Number of messages")
    tows_mod_60_sec = [tow % 60 for tow in messages["tow"]]
    unique_tows, counts = np.unique(tows_mod_60_sec, return_counts=True)
    str_unique_tows = [str(unique_tow) for unique_tow in unique_tows]
    plt.bar(str_unique_tows, counts)


plt.figure()
plt.title("RLS - Messages for satellite and BeaconID")
plt.grid()
plt.ylabel('SVID')
plt.xlabel('ToW')
plt.ylim((0,37))
plt.yticks(np.arange(1, 37), [str(i) for i in np.arange(1, 37)])
for beaconID, messages in rls_by_beaconID.items():
    plt.plot(messages['tow'], messages['svid'], '.', label=f"{beaconID}")
plt.legend(loc='upper right', bbox_to_anchor=(1.05, 1.1), prop={'family':'monospace'})
plt.tight_layout()



plt.show()
        


