import json
import numpy as np
import matplotlib.pyplot as plt

from auxiliar_plot import plot_heatmat_mgs_offset

FILENAME = "./raw_data/2024-07-12.json"
FILENAME = "./raw_data/2024-08-25.json"
FILENAME = "./raw_data/2024-08-24.json"
FILENAME = "./raw_data/2024-11-17.json"
MAX_GAL_SATS = 36
ALL_GAL_SATS = np.arange(1, MAX_GAL_SATS+1)

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

plt.figure(figsize=(9,6))
plt.title(f"RLS - Reception time offset within 2 subframes period")
plt.xlabel("Seconds in GNSS Time")
plt.ylabel("Number of messages")
tows_mod_60_sec = []
for svid in ALL_GAL_SATS:
    tows_mod_60_sec.extend([tow % 60 for tow in rls_by_svid[svid]])
unique_tows, counts = np.unique(tows_mod_60_sec, return_counts=True)
str_unique_tows = [str(unique_tow) for unique_tow in unique_tows]
plt.bar(str_unique_tows, counts)
plt.tight_layout()

plt.figure(figsize=(9,6))
plt.title(f"Orbitography - Reception time offset within 2 subframes period")
plt.xlabel("Seconds in GNSS Time")
plt.ylabel("Number of messages")
tows_mod_60_sec = []
for svid in ALL_GAL_SATS:
    tows_mod_60_sec.extend([tow % 60 for tow in orbitography_by_svid[svid]])
unique_tows, counts = np.unique(tows_mod_60_sec, return_counts=True)
str_unique_tows = [str(unique_tow) for unique_tow in unique_tows]
plt.bar(str_unique_tows, counts)
plt.tight_layout()


plot_heatmat_mgs_offset(orbitography_by_svid.values(),
                        MAX_GAL_SATS,
                        [str(svid) for svid in ALL_GAL_SATS],
                        "SVID",
                        "Orbitography message reception time in 60 seconds modulus (normalized per row)")

plot_heatmat_mgs_offset(rls_by_svid.values(), 
                        MAX_GAL_SATS, 
                        [str(svid) for svid in ALL_GAL_SATS],
                        "SVID",
                        "RLS message reception time in 60 seconds modulus (normalized per row)")


Orb29_RLS = 0
Orb29_noRLS = 0
noOrb29_RLS = 0
noOrb29_noRLS = 0

for svid, orb_tows in orbitography_by_svid.items():
    if svid in [11, 12]:
        continue

    for tow in orb_tows:
        tow_mod60 = tow % 60
        tow_range = range(tow - tow_mod60, tow - tow_mod60 + 60)
        if tow_mod60 == 29:
            if any([1 for rls_tow in rls_by_svid[svid] if rls_tow in tow_range]):
                Orb29_RLS += 1
            else:
                Orb29_noRLS += 1
        else:
            if any([1 for rls_tow in rls_by_svid[svid] if rls_tow in tow_range]):
                noOrb29_RLS += 1
            else:
                noOrb29_noRLS += 1

print(f"""
Orbito at 29, RLS same 60 seconds: {Orb29_RLS}
Orbito at 29, no RLS same 60 seconds: {Orb29_noRLS}
No Orbito at 29, RLS same 60 seconds: {noOrb29_RLS}
No Orbito at 29, no RLS same 60 seconds: {noOrb29_noRLS}      
""")


            





plt.show()
