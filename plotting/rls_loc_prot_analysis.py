import json
import numpy as np
import matplotlib.pyplot as plt

FILENAME = "./raw_data/sept100.json"
#FILENAME = "./ENC25_DATA/ENC25_sar_3_months.json"

with open(FILENAME, 'r') as fd:
    all_sar_json = json.load(fd)

rls_beacon_types = {}
rls_location_prot_by_country_code = {}


for sar_message in all_sar_json:

    if sar_message['message_code']['value'] == "SPARE":
        continue

    if sar_message['beacon_id_parsing_subblock']['protocol_code']['value'] == 'RLS Location Protocol':
        beacon_type = sar_message['beacon_id_parsing_subblock']['beacon_type']['value']
        country_code = sar_message['beacon_id_parsing_subblock']['country_code']['value']
        if beacon_type not in rls_beacon_types:
            rls_beacon_types[beacon_type] = {}
        if country_code not in rls_beacon_types[beacon_type]:
            rls_beacon_types[beacon_type][country_code] = 0
            rls_location_prot_by_country_code[country_code] = 0
        rls_beacon_types[beacon_type][country_code] += 1
        rls_location_prot_by_country_code[country_code] += 1

################################
################################

plt.figure()
plt.title(f"RLS Location Protocol messages received by beacon type")
plt.pie(
    [sum(countries.values()) for countries in rls_beacon_types.values()], 
    labels=rls_beacon_types.keys(), 
    autopct='%1.1f%%',
    textprops={'fontsize': 14}
)
plt.tight_layout()

################################

sorted_items = sorted(rls_location_prot_by_country_code.items(), key=lambda item: item[1], reverse=True)
labels, sizes = zip(*sorted_items)
threshold = 5  # percent
total = sum(sizes)
filtered_labels = [
    label if (value / total * 100) > threshold else ''
    for label, value in zip(labels, sizes)
]
def autopct_format(pct):
    return f'{pct:.1f}%' if pct >= threshold else ''

plt.figure()
plt.title(f"RLS Location Protocol messages received by registration country")
plt.pie(
    sizes, 
    labels=filtered_labels,
    autopct=autopct_format,
    textprops={'fontsize': 15}
)


################################

plt.figure()
plt.title(f"RLS Location Protocol messages received by beacon type and country")

cmap = plt.colormaps["tab20c"]  # 4 variation per colour
outer_colors = cmap([1,4,8])
inner_colors = cmap([2,5,9,10,11])
size = 0.3

total_rls_beacon_types = [sum(countries.values()) for countries in rls_beacon_types.values()]

plt.pie(
    total_rls_beacon_types,
    labels=rls_beacon_types.keys(),
    radius=1,
    autopct='%1.1f%%',
    pctdistance=0.85,
    wedgeprops=dict(width=size, edgecolor='w'),
    textprops={'fontsize': 13}
)

values = [value for countries in rls_beacon_types.values() for value in countries.values()]
labels = [country for countries in rls_beacon_types.values() for country in countries.keys()]
total = sum(values)
filtered_labels = [label if value/total > .05 else '' for value, label in zip(values, labels)]

plt.pie(
    values,
    labels=filtered_labels,
    colors=inner_colors,
    radius=1-size,
    wedgeprops=dict(width=size, edgecolor='w'),
    labeldistance=0.3,
    rotatelabels=True,
    textprops={'fontsize': 13}
)
#plt.tight_layout()

plt.show()
