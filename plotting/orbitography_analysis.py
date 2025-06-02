import json
import numpy as np
import matplotlib.pyplot as plt

from auxiliar_plot import plot_heatmat_mgs_offset

FILENAME = "./raw_data/sept100.json"
#FILENAME = "./SAR_DATA/ENC25_sar_3_months.json"

MAX_GAL_SATS = 36
IGNORE_TRAIL_BITS = True
PLOT_MISC = False

ALL_GAL_SATS = np.arange(1, MAX_GAL_SATS+1)

def plot_messages_for_each_satellite(orbitography_by_svid):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title("Orbitography - Messages from satellite")
    plt.grid()
    plt.ylabel('SVID')
    plt.xlabel('ToW')
    plt.ylim((0,37))
    for svid in ALL_GAL_SATS:
        plt.plot(orbitography_by_svid[svid]['tow'], np.ones(len(orbitography_by_svid[svid]['tow'])) * svid, 'x')

def plot_messages_for_each_satellite_and_ref_beacon(orbitography_by_reference_beacon, country_of_ref_beacon):
    plt.figure()
    plt.title("Orbitography - Messages from satellite and reference beacon")
    plt.grid()
    plt.ylabel('SVID')
    plt.xlabel('ToW')
    plt.ylim((0,37))
    for name, messages in orbitography_by_reference_beacon.items():
        country = country_of_ref_beacon[name]
        plt.plot(messages['tow'], messages['svid'], '.', label=f"{name} - {country}")
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1.1))

def plot_total_messages_for_each_satellite(orbitography_by_svid):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title("Orbitography - Total messages from each satellite")
    plt.ylabel('Number of messages')
    plt.xlabel('SVID')
    number_of_messages = [len(messages['tow']) for messages in orbitography_by_svid.values()]
    plt.bar(ALL_GAL_SATS, number_of_messages)

def plot_total_messages_for_each_satellite_and_ref_beacon(orbitography_by_reference_beacon, country_of_ref_beacon):
    plt.figure()
    plt.title("Orbitography - Total messages from each satellite by reference beacon")
    plt.ylabel('Number of messages', fontsize=13)
    plt.xlabel('SVID', fontsize=13)
    accumulated_by_svid = {svid:0 for svid in ALL_GAL_SATS}
    for name, messages in orbitography_by_reference_beacon.items():
        country = country_of_ref_beacon[name]
        satellites, counts = np.unique(messages['svid'], return_counts=True)
        accumulated_counts = [accumulated_by_svid[svid] for svid in satellites]
        plt.bar(satellites, counts, bottom=accumulated_counts, label=f"{name} - {country}")

        for svid, count in zip(satellites, counts):
            accumulated_by_svid[svid] += count
    plt.xticks(ALL_GAL_SATS, fontsize=13)
    plt.yticks(fontsize=13)
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1))

def plot_messages_for_each_satellite_from_ref_beacon(ref_beacon_msgs, ref_beacon_name, country):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title(f"Orbitography {ref_beacon_name} - {country} - Messages per satellite")
    plt.grid()
    plt.ylabel('SVID')
    plt.xlabel('ToW')
    plt.ylim((0,37))
    plt.plot(ref_beacon_msgs['tow'], ref_beacon_msgs['svid'], '.')

def plot_all_messages_from_ref_beacon(ref_beacon_msgs, ref_beacon_name, country):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title(f"Orbitography {ref_beacon_name} - {country} - Messages over time")
    plt.stem(ref_beacon_msgs['tow'], np.ones(len(ref_beacon_msgs['tow'])))

def plot_histogram_of_time_between_messages_from_ref_beacon(ref_beacon_msgs, ref_beacon_name, country):
    plt.figure()
    plt.title(f"Orbitography {ref_beacon_name} - {country} - Histogram of time between messages")
    plt.xticks(rotation=45)
    time_between_tx = np.diff(ref_beacon_msgs['tow'])
    values, counts = np.unique(time_between_tx, return_counts=True)
    pvalues = [str(value) for value in values]
    plt.bar(pvalues, counts)

def plot_transmission_time_offset_of_messages_from_ref_beacon_in_1min(ref_beacon_msgs, ref_beacon_name, country):
    if not PLOT_MISC:
        return
    plt.figure()
    plt.title(f"Orbitography - Transmission time offset within 2 subframes period - {ref_beacon_name} {country}")
    plt.xlabel("Seconds in GNSS Time")
    plt.ylabel("Number of messages")
    tows_mod_hour = [tow % 60 for tow in ref_beacon_msgs["tow"]]
    unique_tows, counts = np.unique(tows_mod_hour, return_counts=True)
    str_unique_tows = [str(unique_tow) for unique_tow in unique_tows]
    plt.bar(str_unique_tows, counts)

def plot_messages_by_reference_beacon(orbitography_by_reference_beacon: dict):
    plt.figure()
    plt.title(f"Orbitography by reference beacons")
    plt.grid()
    plt.ylabel('Reference Beacons', fontsize=12)
    plt.xlabel('Time of Week', fontsize=12)

    ref_beacon_order = ['MSP-EU4', 'LNC-EU5', 'REU-EU7', 'SON-EU6', 'SMR-EU3', 'TLS-EU1', 'SBG-EU2', 'KLN-EU8', 'V?????E']
    sorted_dict = {}
    for ref_beacon_name in reversed(ref_beacon_order):
        sorted_dict[ref_beacon_name] = orbitography_by_reference_beacon[ref_beacon_name]
    y_values = range(len(sorted_dict))
    y_names = sorted_dict.keys()
    for msgs_dict, y_value in zip(sorted_dict.values(), y_values):
        tows = msgs_dict['tow']
        plt.plot(tows, [y_value]*len(tows), 'x')
    plt.yticks(y_values, y_names, fontsize=12)
    plt.xticks(fontsize=12)


# ================================================= #

if __name__== '__main__':

    orbitography_by_svid = {svid:{'ref_beacon':[], 'tow':[]} for svid in ALL_GAL_SATS}
    orbitography_by_reference_beacon: dict[str, dict[str, list]] = {}
    country_of_ref_beacon = {}

    with open(FILENAME, 'r') as fd:
        all_sar_json = json.load(fd)

    for sar_message in all_sar_json:

        if sar_message['beacon_id_parsing_subblock']['protocol_code']['value'] == 'Orbitography Protocol':
            
            if not IGNORE_TRAIL_BITS and sar_message['beacon_id_parsing_subblock']['trail_bits']['raw_value'] != '0000':
                print(json.dumps(sar_message))
                continue
                #pass

            tow = sar_message['metadata']['tow']
            reference_beacon = sar_message['beacon_id_parsing_subblock']['beacon_id_text']['value']
            country = sar_message['beacon_id_parsing_subblock']['country_code']['value']
            svid = int(sar_message['metadata']['svid'])

            if reference_beacon not in orbitography_by_reference_beacon:
                orbitography_by_reference_beacon[reference_beacon] = {'svid':[], 'tow': []}
                country_of_ref_beacon[reference_beacon] = country
            
            orbitography_by_svid[svid]['ref_beacon'].append(reference_beacon)
            orbitography_by_svid[svid]['tow'].append(tow)
            orbitography_by_reference_beacon[reference_beacon]['svid'].append(svid)
            orbitography_by_reference_beacon[reference_beacon]['tow'].append(tow)

    plot_messages_for_each_satellite(orbitography_by_svid)
    plot_messages_for_each_satellite_and_ref_beacon(orbitography_by_reference_beacon, country_of_ref_beacon)
    plot_total_messages_for_each_satellite(orbitography_by_svid)
    plot_total_messages_for_each_satellite_and_ref_beacon(orbitography_by_reference_beacon, country_of_ref_beacon)
    plot_messages_by_reference_beacon(orbitography_by_reference_beacon)
    plot_heatmat_mgs_offset([ref_beacon["tow"] for ref_beacon in orbitography_by_reference_beacon.values()],
                            len(orbitography_by_reference_beacon),
                            orbitography_by_reference_beacon,
                            "Reference beacons",
                            "Orbitography message transmission time in 60 seconds modulus by reference beacon",
                            "Caption")

    # for ref_beacon_name, ref_beacon_msgs in orbitography_by_reference_beacon.items():
    #     country = country_of_ref_beacon[ref_beacon_name]
    #     plot_messages_for_each_satellite_from_ref_beacon(ref_beacon_msgs, ref_beacon_name, country)
    #     plot_all_messages_from_ref_beacon(ref_beacon_msgs, ref_beacon_name, country)
    #     plot_histogram_of_time_between_messages_from_ref_beacon(ref_beacon_msgs, ref_beacon_name, country)
    #     plot_transmission_time_offset_of_messages_from_ref_beacon_in_1min(ref_beacon_msgs, ref_beacon_name, country)

    plt.show()
