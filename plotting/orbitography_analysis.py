import json
import numpy as np
import matplotlib.pyplot as plt
from copy import copy

from auxiliar_plot import plot_heatmat_mgs_offset


FILENAME = "./raw_data/2024-07-12.json"
MAX_GAL_SATS = 36
IGNORE_TRAIL_BITS = False
PLOT_MISC = False

ALL_GAL_SATS = np.arange(1, MAX_GAL_SATS+1)

def plot_messages_for_each_satellite(orbitography_by_svid):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title("Orbitography - Messages for satellite")
    plt.grid()
    plt.ylabel('SVID')
    plt.xlabel('ToW')
    plt.ylim((0,37))
    for svid in ALL_GAL_SATS:
        plt.plot(orbitography_by_svid[svid]['tow'], np.ones(len(orbitography_by_svid[svid]['tow'])) * svid, 'x')

def plot_messages_for_each_satellite_and_station(orbitography_by_ground_station, country_of_station):
    plt.figure()
    plt.title("Orbitography - Messages for satellite and ground station")
    plt.grid()
    plt.ylabel('SVID')
    plt.xlabel('ToW')
    plt.ylim((0,37))
    for name, messages in orbitography_by_ground_station.items():
        country = country_of_station[name]
        plt.plot(messages['tow'], messages['svid'], '.', label=f"{name} - {country}")
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1.1))

def plot_total_messages_for_each_satellite(orbitography_by_svid):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title("Orbitography - Total messages for each satellite")
    plt.ylabel('Number of messages')
    plt.xlabel('SVID')
    number_of_messages = [len(messages['tow']) for messages in orbitography_by_svid.values()]
    plt.bar(ALL_GAL_SATS, number_of_messages)

def plot_total_messages_for_each_satellite_and_station(orbitography_by_ground_station, country_of_station):
    plt.figure()
    plt.title("Orbitography - Total messages for each satellite by ground station")
    plt.ylabel('Number of messages')
    plt.xlabel('SVID')
    accumulated_by_svid = {svid:0 for svid in ALL_GAL_SATS}
    for name, messages in orbitography_by_ground_station.items():
        country = country_of_station[name]
        satellites, counts = np.unique(messages['svid'], return_counts=True)
        accumulated_counts = [accumulated_by_svid[svid] for svid in satellites]
        plt.bar(satellites, counts, bottom=accumulated_counts, label=f"{name} - {country}")

        for svid, count in zip(satellites, counts):
            accumulated_by_svid[svid] += count
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1))

def plot_messages_for_each_satellite_from_base_station(station_msgs, station_name, country):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title(f"Orbitography {station_name} - {country} - Messages per satellite")
    plt.grid()
    plt.ylabel('SVID')
    plt.xlabel('ToW')
    plt.ylim((0,37))
    plt.plot(station_msgs['tow'], station_msgs['svid'], '.')

def plot_all_messages_from_base_station(station_msgs, station_name, country):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title(f"Orbitography {station_name} - {country} - Messages over time")
    plt.stem(station_msgs['tow'], np.ones(len(station_msgs['tow'])))

def plot_histogram_of_time_between_messages_from_base_station(station_msgs, station_name, country):
    plt.figure()
    plt.title(f"Orbitography {station_name} - {country} - Histogram of time between messages")
    plt.xticks(rotation=45)
    time_between_tx = np.diff(station_msgs['tow'])
    values, counts = np.unique(time_between_tx, return_counts=True)
    pvalues = [str(value) for value in values]
    plt.bar(pvalues, counts)

def plot_reception_time_offset_of_messages_from_base_station_in_1min(station_msgs, station_name, country):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title(f"Orbitography - Reception time offset within 2 subframes period - {station_name} {country}")
    plt.xlabel("Seconds in GNSS Time")
    plt.ylabel("Number of messages")
    tows_mod_hour = [tow % 60 for tow in station_msgs["tow"]]
    unique_tows, counts = np.unique(tows_mod_hour, return_counts=True)
    str_unique_tows = [str(unique_tow) for unique_tow in unique_tows]
    plt.bar(str_unique_tows, counts)

# ================================================= #

if __name__== '__main__':

    orbitography_by_svid = {svid:{'station':[], 'tow':[]} for svid in ALL_GAL_SATS}
    orbitography_by_ground_station: dict[str, dict[str, list]] = {}
    country_of_station = {}

    with open(FILENAME, 'r') as fd:
        all_sar_json = json.load(fd)

    for sar_message in all_sar_json:

        if sar_message['beacon_id_parsing_subblock']['protocol_code']['value'] == 'Orbitography Protocol':
            
            if not IGNORE_TRAIL_BITS and sar_message['beacon_id_parsing_subblock']['trail_bits']['raw_value'] != '0000':
                #print(json.dumps(sar_message))
                #continue
                pass

            tow = sar_message['metadata']['tow']
            ground_station = sar_message['beacon_id_parsing_subblock']['beacon_id_text']['value']
            country = sar_message['beacon_id_parsing_subblock']['country_code']['value']
            svid = int(sar_message['metadata']['svid'])

            if ground_station not in orbitography_by_ground_station:
                orbitography_by_ground_station[ground_station] = {'svid':[], 'tow': []}
                country_of_station[ground_station] = country
            
            orbitography_by_svid[svid]['station'].append(ground_station)
            orbitography_by_svid[svid]['tow'].append(tow)
            orbitography_by_ground_station[ground_station]['svid'].append(svid)
            orbitography_by_ground_station[ground_station]['tow'].append(tow)

    plot_messages_for_each_satellite(orbitography_by_svid)
    plot_messages_for_each_satellite_and_station(orbitography_by_ground_station, country_of_station)
    plot_total_messages_for_each_satellite(orbitography_by_svid)
    plot_total_messages_for_each_satellite_and_station(orbitography_by_ground_station, country_of_station)
    plot_heatmat_mgs_offset([station["tow"] for station in orbitography_by_ground_station.values()],
                            len(orbitography_by_ground_station),
                            orbitography_by_ground_station,
                            "Ground Stations",
                            "Orbitography message reception time in 60 seconds modulus by ground station")


    for station_name, station_msgs in orbitography_by_ground_station.items():
        country = country_of_station[station_name]
        plot_messages_for_each_satellite_from_base_station(station_msgs, station_name, country)
        plot_all_messages_from_base_station(station_msgs, station_name, country)
        plot_histogram_of_time_between_messages_from_base_station(station_msgs, station_name, country)
        plot_reception_time_offset_of_messages_from_base_station_in_1min(station_msgs, station_name, country)

    plt.show()
