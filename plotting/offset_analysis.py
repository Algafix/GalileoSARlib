import json
import numpy as np
import matplotlib.pyplot as plt
from copy import copy

FILENAME = "./raw_data/2024-07-12.json"
MAX_GAL_SATS = 36
ALL_GAL_SATS = np.arange(1, MAX_GAL_SATS+1)

def heatmat_norm_by_row(sar_messages_dict, max_y_axis):
    total_messages = np.zeros((max_y_axis, 30))
    for svid in np.arange(max_y_axis):
        tows_mod_60_sec = [tow % 60 for tow in sar_messages_dict[svid+1]]
        unique_tows, counts = np.unique(tows_mod_60_sec, return_counts=True)
        for tow, count in zip(unique_tows, counts):
            total_messages[svid][tow//2] = count

    rows_shift_to_0 = (total_messages - np.min(total_messages, axis=1)[:, np.newaxis])
    rows_max_magnitude = np.ptp(total_messages, axis=1)[:, np.newaxis]
    row_normalized_total_messages = np.divide(rows_shift_to_0, rows_max_magnitude, out=np.zeros(total_messages.shape), where=rows_max_magnitude!=0) 

    return row_normalized_total_messages

with open(FILENAME, 'r') as fd:
    all_sar_json = json.load(fd)

orbitography_by_svid = {svid:[] for svid in ALL_GAL_SATS}
rls_by_svid = {svid:[] for svid in ALL_GAL_SATS}

for sar_message in all_sar_json:
    protocol = sar_message['beacon_id_parsing_subblock']['protocol_code']['value']
    svid = int(sar_message['metadata']['svid'])
    tow = sar_message['metadata']['tow']

    if protocol == 'RLS Location Protocol':
        rls_by_svid[svid].append(tow)
    elif protocol == 'Orbitography Protocol':
        orbitography_by_svid[svid].append(tow)
    else:
        print(f"Protocol not contemplated! {protocol}")
        continue

plt.figure()
plt.title(f"RLS - Reception time offset within 2 subframes period")
plt.xlabel("Seconds in GNSS Time")
plt.ylabel("Number of messages")
tows_mod_60_sec = []
for svid in ALL_GAL_SATS:
    tows_mod_60_sec.extend([tow % 60 for tow in rls_by_svid[svid]])
unique_tows, counts = np.unique(tows_mod_60_sec, return_counts=True)
str_unique_tows = [str(unique_tow) for unique_tow in unique_tows]
plt.bar(str_unique_tows, counts)

plt.figure()
plt.title(f"Orbitography - Reception time offset within 2 subframes period")
plt.xlabel("Seconds in GNSS Time")
plt.ylabel("Number of messages")
tows_mod_60_sec = []
for svid in ALL_GAL_SATS:
    tows_mod_60_sec.extend([tow % 60 for tow in orbitography_by_svid[svid]])
unique_tows, counts = np.unique(tows_mod_60_sec, return_counts=True)
str_unique_tows = [str(unique_tow) for unique_tow in unique_tows]
plt.bar(str_unique_tows, counts)

log_cmap = copy(plt.get_cmap('viridis'))
log_cmap.set_bad(log_cmap(0))

plt.figure(figsize=(9,6))
plt.title(f"Orbitography message reception time in 60 seconds modulus (normalized per row)")
row_normalized_total_messages = heatmat_norm_by_row(orbitography_by_svid, MAX_GAL_SATS)
plt.pcolormesh(row_normalized_total_messages, cmap=log_cmap, edgecolors='k', linewidths=0.5)
#plt.pcolormesh(row_normalized_total_messages, cmap=log_cmap, edgecolors='k', linewidths=0.5, norm='log')
plt.yticks(np.arange(MAX_GAL_SATS) + 0.5, [str(svid) for svid in ALL_GAL_SATS])
plt.xticks(np.arange(30) + 0.5, [str(i) for i in np.arange(1,61,2)])
plt.ylabel(f"SVID")
plt.xlabel(f"Reception time of the last page of the SAR message (s)")
plt.tight_layout()
plt.colorbar()

plt.figure(figsize=(9,6))
plt.title(f"RLS message reception time in 60 seconds modulus (normalized per row)")
row_normalized_total_messages = heatmat_norm_by_row(rls_by_svid, MAX_GAL_SATS)
plt.pcolormesh(row_normalized_total_messages, cmap=log_cmap, edgecolors='k', linewidths=0.5)
#plt.pcolormesh(row_normalized_total_messages, cmap=log_cmap, edgecolors='k', linewidths=0.5, norm='log')
plt.yticks(np.arange(MAX_GAL_SATS) + 0.5, [str(svid) for svid in ALL_GAL_SATS])
plt.xticks(np.arange(30) + 0.5, [str(i) for i in np.arange(1,61,2)])
plt.ylabel(f"SVID")
plt.xlabel(f"Reception time of the last page of the SAR message (s)")
plt.tight_layout()
plt.colorbar()

plt.show()
