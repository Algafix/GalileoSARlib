import json
import numpy as np
import matplotlib.pyplot as plt

from auxiliar_plot import plot_heatmat_mgs_offset, plot_histogram_msg_offset

FILENAME = "./raw_data/sept100.json"
#FILENAME = "./ENC25_DATA/ENC25_sar_3_months.json"

MAX_GAL_SATS = 36
ALL_GAL_SATS = np.arange(1, MAX_GAL_SATS+1)

with open(FILENAME, 'r') as fd:
    all_sar_json = json.load(fd)

short_spare_by_svid = {svid:[] for svid in ALL_GAL_SATS}
short_orbitography_by_svid = {svid:[] for svid in ALL_GAL_SATS}
short_rls_loc_by_svid = {svid:[] for svid in ALL_GAL_SATS}
long_spare_by_svid = {svid:[] for svid in ALL_GAL_SATS}

for sar_message in all_sar_json:

    # Some strange test messages, skip further processing if thats the case
    if sar_message['beacon_id']['raw_value'][:5] == 'aaaaa':
        continue
    
    svid = int(sar_message['metadata']['svid'])
    tow = sar_message['metadata']['tow']

    if sar_message['rlm_id']['value'] == 'SHORT_RLM':
        # Short RLM messages
        if sar_message['message_code']['value'] == 'SPARE':
            short_spare_by_svid[svid].append(tow)
        else:
            protocol = sar_message['beacon_id_parsing_subblock']['protocol_code']['value']
            if protocol == 'RLS Location Protocol':
                short_rls_loc_by_svid[svid].append(tow)
            elif protocol == 'Orbitography Protocol':
                short_orbitography_by_svid[svid].append(tow)
            else:
                print(f"Protocol not contemplated! {protocol}")
    else:
        # Long RLM messages
        if sar_message['message_code']['value'] == 'SPARE':
            long_spare_by_svid[svid].append(tow)
        else:
            print(f"Message code for Long RLM not spare! {sar_message['message_code']['value']}")

plot_histogram_msg_offset(short_spare_by_svid,
                          "Short RLM Spare - Transmission time offset within 2 subframes period")

plot_histogram_msg_offset(short_rls_loc_by_svid,
                          "RLS Location - Transmission time offset within 2 subframes period")

plot_histogram_msg_offset(short_orbitography_by_svid,
                          "Orbitography - Transmission time offset within 2 subframes period")

plot_histogram_msg_offset(long_spare_by_svid,
                          "Long RLM Spare - Transmission time offset within 2 subframes period")

plot_heatmat_mgs_offset(short_spare_by_svid.values(),
                        MAX_GAL_SATS,
                        [str(svid) for svid in ALL_GAL_SATS],
                        "SVID",
                        "Short RLM Spare message trasmission time in 60 seconds modulus",
                        "Caption: ",
                        log_norm=True)

plot_heatmat_mgs_offset(short_orbitography_by_svid.values(),
                        MAX_GAL_SATS,
                        [str(svid) for svid in ALL_GAL_SATS],
                        "SVID",
                        "Orbitography message trasmission time in 60 seconds modulus",
                        "Caption: All satellites send the messages for the Orbitography protocol on the second 29 but SVID 11 and 12, which are also the oldest satellites",
                        log_norm=True)

plot_heatmat_mgs_offset(short_rls_loc_by_svid.values(), 
                        MAX_GAL_SATS, 
                        [str(svid) for svid in ALL_GAL_SATS],
                        "SVID",
                        "RLS Location message transmission time in 60 seconds modulus",
                        "Caption: All satellites send the messages for the RLS protocol on the second 13 but SVID 11 and 12, which are also the oldest satellites",
                        log_norm=True)

plot_heatmat_mgs_offset(long_spare_by_svid.values(),
                        MAX_GAL_SATS,
                        [str(svid) for svid in ALL_GAL_SATS],
                        "SVID",
                        "Long RLM reception time in 60 seconds modulus",
                        "Caption: ",
                        log_norm=True)

# Check if the reason for deviation in Orbitography is the transmission of a RLM Location in the same minute
# Orb23_RLS = 0
# Orb23_noRLS = 0
# noOrb23_RLS = 0
# noOrb23_noRLS = 0

# for svid, orb_tows in short_orbitography_by_svid.items():
#     if svid in [11, 12]:
#         continue

#     for tow in orb_tows:
#         tow_mod60 = tow % 60
#         tow_range = range(tow - tow_mod60, tow - tow_mod60 + 60)
#         if tow_mod60 == 23:
#             if any([1 for rls_tow in short_rls_loc_by_svid[svid] if rls_tow in tow_range]):
#                 Orb23_RLS += 1
#             else:
#                 Orb23_noRLS += 1
#         else:
#             if any([1 for rls_tow in short_rls_loc_by_svid[svid] if rls_tow in tow_range]):
#                 noOrb23_RLS += 1
#             else:
#                 noOrb23_noRLS += 1

# print(f"""
# Orbito at 23, RLS same 60 seconds: {Orb23_RLS}
# Orbito at 23, no RLS same 60 seconds: {Orb23_noRLS}
# No Orbito at 23, RLS same 60 seconds: {noOrb23_RLS}
# No Orbito at 23, no RLS same 60 seconds: {noOrb23_noRLS}      
# """)


plt.show()
