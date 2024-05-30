
def print_sar_message(sar_message: dict, tab='\t'):
    for key, block in sar_message.items():
        if key == 'metadata':
            print(f"{block['wn']} {block['tow']} - {block['svid']} SAR MESSAGE")
        else:
            try:
                if 'subblock' in key:
                    print_sar_message(block, tab+'\t')
                elif 'value' in block and 'raw_value' in block:
                    print(f"{tab}{block['name']}: {block['value']} ({block['raw_value']})")
                elif 'raw_value' in block:
                    print(f"{tab}{block['name']}: {block['raw_value']}")
                elif 'value' in block:
                    print(f"{tab}{block['name']}: {block['value']}")
            except Exception:
                print(f"{tab}{key}: None")

BASE_SAR_MESSAGE = {
    'metadata' : {},
    'rlm_id': {
        'name': 'RLM Identifier',
    },
    'beacon_id': {
        'name': 'Beacon ID',
    },
    'message_code': {
        'name': 'Message Code',
    },
    'rlm_params': {
        'name': 'SRL Parameters',
    },
    'beacon_id_parsing_subblock': None,
}

BASE_BEACON_ID = {
    'protocol_flag': {
        'name': 'Protocol Type',
    },
    'country_code': {
        'name': 'Country Code',
    },
    'protocol_code': {
        'name': 'Protocol Code',
    },
}

RLS_LOCATION_PROTOCOL = {
    'beacon_type': {
        'name': 'Beacon Type',
    },
    'trunc_tac': {
        'name': 'C/S RLS TAC (trunc)',
    },
    'tac': {
        'name': 'C/S RLS TAC',
    },
    'tac_subblock': {
        'manufacturer': {
            'name': 'Manufacturer',
        },
        'model_name': {
            'name': 'Model',
        },
        'last_rev_date': {
            'name': 'Last rev. Date',
        },
        'navigation': {
            'name': 'Nav Info',
        },
    },
    'serial_num': {
        'name': 'Serial Number',
    },
    'truncated_mmsi': {
        'name': '6-digit MMSI',
    },
    'lat': {
        'name': 'Lat',
    },
    'lon': {
        'name': 'Lon',
    },
}

ORBITOGRAPHY_PROTOCOL = {
    'beacon_id_text': {
        'name': 'Orbitography Beacon ID',
    },
    'trail_bits': {
        'name': 'Four Zeros',
    }
}

