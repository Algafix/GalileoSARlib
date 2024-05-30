import json
import csv

def clean_cell(cell_value: str):
    return cell_value[2:-1]

csv_file = open('TAC_models.csv', 'r')
out_json_file = open('TAC_models.json', 'w')
tac_dict = {}

tac_csv_reader = csv.DictReader(csv_file)

for row in tac_csv_reader:
    tac_num = clean_cell(row['="C/S TAC No."'])
    tac_dict[tac_num] = {
        "tac_num": tac_num,
        "model_name": clean_cell(row['="Beacon Model Name"']),
        "manufacturer": clean_cell(row['="Manufacturer"']),
        "beacon_type": clean_cell(row['="Beacon type"']),
        "last_rev_date": clean_cell(row['="Last Rev. Date"']),
        "issue_date": clean_cell(row['="Issue date"']),
        "navigation": clean_cell(row['="nav int/ext"']),
    }

json.dump(tac_dict, out_json_file, indent=2)

csv_file.close()
out_json_file.close()