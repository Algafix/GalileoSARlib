import json
from enum import Enum
from bitstring import BitArray
from aux.mod_baudot_code import MOD_BAUDOT_CODE
from aux.json_templates import BASE_BEACON_ID, RLS_LOCATION_PROTOCOL, ORBITOGRAPHY_PROTOCOL

with open('./aux/ITU_MID.json', 'r') as itu_mid_file:
    # https://www.itu.int/en/ITU-R/terrestrial/fmd/Pages/mid.aspx
    ITU_MID = json.load(itu_mid_file)

with open('./aux/TAC_models.json', 'r') as tac_models_file:
    # https://406registration.com/approved-tac
    TAC_MODELS = json.load(tac_models_file)

class PROTOCOL_FLAG(Enum):
    STANDARD_OR_NATIONAL = 0
    USER_PROTOCOLS = 1

PROTOCOL_FLAG_lt = {
    PROTOCOL_FLAG.STANDARD_OR_NATIONAL: 'Standard or national location protocols',
    PROTOCOL_FLAG.USER_PROTOCOLS: 'User or user-location protocols',
}

BEACON_TYPE_lt = {
    '00':'ELT',
    '01':'EPIRB',
    '10':'PLB',
    '11':'Location Test Protocol',
}

BEACON_TYPE_MMSI_lt = {
    '00':'First EPIRB on Vessel',
    '01':'Second EPIRB on Vessel',
    '10':'PLB',
    '11':'Location Test Protocol',
}

TAC_PREFIX_lt = {
    'EPIRB': '1',
    'ELT': '2',
    'PLB': '3',
    'Location Test Protocol': 'X'
}

LAT = {0:'N', 1:'S'}
LON = {0:'E', 1:'W'}

def parse_country_code(country_code_bits: BitArray):
    country_code = country_code_bits.uint
    try:
        country_code_name = ITU_MID[str(country_code)]
    except KeyError:
        country_code_name = "Unknown"
    return country_code, country_code_name

def parse_RLS_location_protocol(beacon_id: BitArray):
    rls_loc_dict = dict(RLS_LOCATION_PROTOCOL)

    is_mmsi = (beacon_id[17:21].bin == '1111')

    if is_mmsi:
        truncated_MMSI = beacon_id[21:41]
        rls_loc_dict['beacon_type']['value'] = BEACON_TYPE_MMSI_lt[beacon_id[15:17].bin]
        rls_loc_dict['beacon_type']['raw_value'] = beacon_id[15:17].bin
        rls_loc_dict['truncated_mmsi']['value'] = truncated_MMSI.uint
        rls_loc_dict['truncated_mmsi']['raw_value'] = truncated_MMSI.bin
    else:
        beacon_type_bin = beacon_id[15:17].bin
        beacon_type_str = BEACON_TYPE_lt[beacon_type_bin]
        truncated_cs_rls_tac = beacon_id[17:27]
        prod_serial_number = beacon_id[27:41]
        full_tac = f"{TAC_PREFIX_lt[beacon_type_str]}{truncated_cs_rls_tac.uint}"
        beacon_info = TAC_MODELS[full_tac]
        rls_loc_dict['beacon_type']['value'] = beacon_type_str
        rls_loc_dict['beacon_type']['raw_value'] = beacon_type_bin
        rls_loc_dict['trunc_tac']['value'] = truncated_cs_rls_tac.uint
        rls_loc_dict['trunc_tac']['raw_value'] = truncated_cs_rls_tac.bin
        rls_loc_dict['tac']['value'] = full_tac
        rls_loc_dict['tac_subblock']['manufacturer']['value'] = beacon_info['manufacturer']
        rls_loc_dict['tac_subblock']['model_name']['value'] = beacon_info['model_name']
        rls_loc_dict['tac_subblock']['last_rev_date']['value'] = beacon_info['last_rev_date']
        rls_loc_dict['tac_subblock']['navigation']['value'] = beacon_info['navigation']
        rls_loc_dict['serial_num']['value'] = prod_serial_number.uint
        rls_loc_dict['serial_num']['raw_value'] = prod_serial_number.bin

    lat = beacon_id[41]
    lat_degrees = beacon_id[42:50] 
    lon = beacon_id[50]
    lon_degrees = beacon_id[51:]
    rls_loc_dict['lat']['value'] = f"{LAT[lat]} {lat_degrees.uint}"
    rls_loc_dict['lat']['raw_value'] = f"{int(lat)} {lat_degrees.bin}"
    rls_loc_dict['lon']['value'] = f"{LON[lon]} {lon_degrees.uint}"
    rls_loc_dict['lon']['raw_value'] = f"{int(lon)} {lon_degrees.bin}"

    return rls_loc_dict

def parse_orbitography_protocol(beacon_id: BitArray):
    orbitography_dict = dict(ORBITOGRAPHY_PROTOCOL)

    seven_char_id = beacon_id[14:56]
    last_four_zeros = beacon_id[56:]
    cleartext_char_list = []
    for chunk in seven_char_id.cut(6):
        try:
            cleartext_char_list.append(MOD_BAUDOT_CODE[chunk.bin])
        except KeyError:
            cleartext_char_list.append('?')
    cleartext_char_id = ''.join(cleartext_char_list)

    orbitography_dict['beacon_id_text']['value'] = cleartext_char_id
    orbitography_dict['beacon_id_text']['raw_value'] = seven_char_id.bin
    orbitography_dict['trail_bits']['raw_value'] = last_four_zeros.bin

    return orbitography_dict

def not_implemented(beacon_id: BitArray):
    pass

PROTOCOL_CODES = {
    "000":
    {
        "name": "Orbitography Protocol",
        "parse_function": parse_orbitography_protocol,
    },
    "1110":
    {
        "name": "Standard Test Location Protocol",
        "parse_function": not_implemented,
    },
    "1111":
    {
        "name": "National Test Location Protocol",
        "parse_function": not_implemented,
    },
    "1101":
    {
        "name": "RLS Location Protocol",
        "parse_function": parse_RLS_location_protocol,
    },
    "unknown":
    {
        "name": "Unknown",
        "parse_function": not_implemented,
    }
}

def parse_beacon_id(beacon_id: BitArray):
    beacon_id_dict = dict(BASE_BEACON_ID)

    protocol_flag = PROTOCOL_FLAG(beacon_id[0])
    country_code, country_code_name = parse_country_code(beacon_id[1:11])

    if protocol_flag == PROTOCOL_FLAG.STANDARD_OR_NATIONAL:
        protocol_code_bits = beacon_id[11:15].bin
    else:
        protocol_code_bits = beacon_id[11:14].bin

    try:
        protocol_code  = PROTOCOL_CODES[protocol_code_bits]
    except KeyError:
        protocol_code = PROTOCOL_CODES["unknown"]

    beacon_id_dict['protocol_flag']['value'] = PROTOCOL_FLAG_lt[protocol_flag]
    beacon_id_dict['protocol_flag']['raw_value'] = protocol_flag.value
    beacon_id_dict['country_code']['value'] = country_code_name
    beacon_id_dict['country_code']['raw_value'] = country_code
    beacon_id_dict['protocol_code']['value'] = protocol_code['name']
    beacon_id_dict['protocol_code']['raw_value'] = protocol_code_bits

    beacon_id_dict.update(protocol_code['parse_function'](beacon_id))

    return beacon_id_dict
