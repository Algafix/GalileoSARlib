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

with open("./raw_data/2024-07-12.json", 'r') as fd:
    all_sar_json = json.load(fd)

all_orbitography_list = []
orbitography_per_station_and_sat = {}
orbitography_per_station = {}
country_of_station = {}
for sar_message in all_sar_json:
    if sar_message['beacon_id_parsing_subblock']['protocol_code']['value'] == 'Orbitography Protocol':
        
        if sar_message['beacon_id_parsing_subblock']['trail_bits']['raw_value'] != '0000':
            #print(json.dumps(sar_message))
            #continue
            pass
        
        tow = sar_message['metadata']['tow']
        all_orbitography_list.append(tow)

        ground_station = sar_message['beacon_id_parsing_subblock']['beacon_id_text']['value']
        country = sar_message['beacon_id_parsing_subblock']['country_code']['value']
        svid = sar_message['metadata']['svid']

        if ground_station not in orbitography_per_station:
            orbitography_per_station[ground_station] = []
            orbitography_per_station_and_sat[ground_station] = {}
            country_of_station[ground_station] = country
        
        station_dict = orbitography_per_station_and_sat[ground_station]

        if svid not in station_dict:
            station_dict[svid] = []

        orbitography_per_station[ground_station].append(tow)
        station_dict[svid].append(tow)


# all_tx_tows_for_station = orbitography_per_station['GAL-EU6']

# time_between_tx = np.diff(all_tx_tows_for_station)
# values, counts = np.unique(time_between_tx, return_counts=True)

# plt.figure()
# pvalues = [str(value) for value in values]
# plt.bar(pvalues, counts)
# plt.xticks(rotation=45)
# plt.title("GAL-EU6 - Denmark - Histogram of time between messages")

# plt.figure()
# plt.title("GAL-EU6 - Denmark - Messages over time")
# plt.stem(all_tx_tows_for_station, np.ones(len(all_tx_tows_for_station)))

# plt.figure()
# plt.title("GAL-EU6 - Denmark - Messages per satellite")
# plt.grid()
# plt.ylabel('SVID')
# plt.xlabel('ToW')
# plt.ylim((0,37))

# base_station = orbitography_per_station_and_sat['GAL-EU6']
# for svid in np.arange(1, MAX_GAL_SATS+1):
#     s_svid = f"{svid:02d}"
#     if s_svid in base_station:
#         plt.plot(base_station[s_svid], np.ones(len(base_station[s_svid])) * svid, '.')


for base_station, base_station_svids in orbitography_per_station_and_sat.items():

    country = country_of_station[base_station]
    all_tx_tows_for_station = orbitography_per_station[base_station]

    plt.figure()
    plt.title(f"Orbitography {base_station} - {country} - Messages over time")
    plt.stem(all_tx_tows_for_station, np.ones(len(all_tx_tows_for_station)))


    time_between_tx = np.diff(all_tx_tows_for_station)
    values, counts = np.unique(time_between_tx, return_counts=True)

    plt.figure()
    pvalues = [str(value) for value in values]
    plt.bar(pvalues, counts)
    plt.xticks(rotation=45)
    plt.title(f"Orbitography {base_station} - {country} - Histogram of time between messages")


    plt.figure()
    plt.title(f"Orbitography {base_station} - {country} - Messages per satellite")
    plt.grid()
    plt.ylabel('SVID')
    plt.xlabel('ToW')
    plt.ylim((0,37))

    for svid in np.arange(1, MAX_GAL_SATS+1):
        s_svid = f"{svid:02d}"
        if s_svid in base_station_svids:
            plt.plot(base_station_svids[s_svid], np.ones(len(base_station_svids[s_svid])) * svid, '.')


plt.show()