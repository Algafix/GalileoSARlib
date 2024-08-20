#
# Plot information about the Orbitography messages grouped by satellite number
# - Time plot of orbitography messages for each satellite
# - Time plot of orbitography messages for each satellite colored by ground station
# - Number of messages for each satellite
# - Number of messages for each satellite by ground station
# - Time when the ground stations send the messages
###########################################################################

import json

import numpy as np
import matplotlib.pyplot as plt

MAX_GAL_SATS = 36

all_gal_sats = np.arange(1, MAX_GAL_SATS+1)
sar_by_svid = {svid:[] for svid in all_gal_sats}
sar_by_ground_station = {}
country_of_station = {}

with open("./raw_data/2024-07-12.json", 'r') as fd:
    all_sar_json = json.load(fd)

for sar_message in all_sar_json:
    if sar_message['beacon_id_parsing_subblock']['protocol_code']['value'] == 'Orbitography Protocol':
        
        if sar_message['beacon_id_parsing_subblock']['trail_bits']['raw_value'] != '0000':
            #print(json.dumps(sar_message))
            #continue
            pass
        
        tow = sar_message['metadata']['tow']
        ground_station = sar_message['beacon_id_parsing_subblock']['beacon_id_text']['value']
        country = sar_message['beacon_id_parsing_subblock']['country_code']['value']
        svid = int(sar_message['metadata']['svid'])
        if ground_station not in sar_by_ground_station:
            sar_by_ground_station[ground_station] = {'svid':[], 'tow': []}
            country_of_station[ground_station] = country

        sar_by_svid[svid].append(tow)
        sar_by_ground_station[ground_station]['svid'].append(svid)
        sar_by_ground_station[ground_station]['tow'].append(tow)

plt.figure()
plt.title("Orbitography - Messages per satellite")
plt.grid()
plt.ylabel('SVID')
plt.xlabel('ToW')
plt.ylim((0,37))
for svid in all_gal_sats:
    plt.plot(sar_by_svid[svid], np.ones(len(sar_by_svid[svid])) * svid, 'x')

plt.figure()
plt.title("Orbitography - Messages per satellite and ground station")
plt.grid()
plt.ylabel('SVID')
plt.xlabel('ToW')
plt.ylim((0,37))
for name, messages in sar_by_ground_station.items():
    country = country_of_station[name]
    plt.plot(messages['tow'], messages['svid'], '.', label=f"{name} - {country}")
plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1.1))

plt.figure()
plt.title("Orbitography - Total messages for each satellite")
plt.ylabel('Number of messages')
plt.xlabel('SVID')
number_of_messages = [len(messages) for messages in sar_by_svid.values()]
plt.bar(all_gal_sats, number_of_messages)

plt.figure()
plt.title("Orbitography - Total messages for each satellite by ground station")
plt.ylabel('Number of messages')
plt.xlabel('SVID')
accumulated_by_svid = {svid:0 for svid in all_gal_sats}
for name, messages in sar_by_ground_station.items():
    country = country_of_station[name]
    satellites, counts = np.unique(messages['svid'], return_counts=True)
    accumulated_counts = [accumulated_by_svid[svid] for svid in satellites]
    plt.bar(satellites, counts, bottom=accumulated_counts, label=f"{name} - {country}")

    for svid, count in zip(satellites, counts):
        accumulated_by_svid[svid] += count
plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1))


for station_name, station in sar_by_ground_station.items():
    country = country_of_station[name]
    tows_mod_hour = [(tow-18) % 60 for tow in station["tow"]]
    unique_tows, counts = np.unique(tows_mod_hour, return_counts=True)
    str_unique_tows = [str(unique_tow) for unique_tow in unique_tows]
    plt.figure()
    plt.title(f"Orbitography - Message offset in 1 minute - {station_name} {country}")
    plt.xlabel("Seconds in UTC (18 leap seconds wrt gnss)")
    plt.ylabel("Number of messages")
    plt.bar(str_unique_tows, counts)


plt.show()
