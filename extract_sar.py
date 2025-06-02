import argparse
import json
from copy import deepcopy
from bitstring import BitArray

from input_modules.input_sbf import SBF
from input_modules.base_class import SARFormat
from aux.protocol_parsing import parse_beacon_id
from aux.aux_classes import RLM, MESSAGE_CODES, GST
from aux.json_templates import print_sar_message, BASE_SAR_MESSAGE

class SARMessage:
    
    def __init__(self, svid: int) -> None:
        self.current_message = BitArray()
        self.rlm_id = RLM(0)
        self.start_gst = GST(wn=0, tow=0)
        self.last_gst = GST(wn=0, tow=0)
        self.svid = svid

    def _start_message(self, sar_data: SARFormat):
        self.current_message.clear()
        self.rlm_id = sar_data.rlm_id
        self.start_gst = sar_data.gst
        self.last_gst = sar_data.gst
        self.current_message.append(sar_data.rlm_data)

    def _is_sync(self, sar_data: SARFormat) -> bool:
        return (sar_data.gst == self.last_gst + 2) and (sar_data.rlm_id == self.rlm_id)

    def _is_complete(self):
        return (self.rlm_id == RLM.SHORT_RLM and len(self.current_message) == 80 or 
                self.rlm_id == RLM.LONG_RLM and len(self.current_message) == 160)

    def new_sar_data(self, sar_data: SARFormat):

        if sar_data.start_bit:
            self._start_message(sar_data)
            return None
        if not self._is_sync(sar_data):
            return None

        self.current_message.append(sar_data.rlm_data)
        self.last_gst = sar_data.gst

        if self._is_complete():
            return self._parse_SAR_message()

    def _parse_SAR_message(self):

        beacon_id = self.current_message[:60]
        message_code = MESSAGE_CODES(self.current_message[60:64].bin)
        SRLM_params = self.current_message[64:]

        sar_message_dict = deepcopy(BASE_SAR_MESSAGE)
        sar_message_dict['metadata']['wn'] = self.start_gst.wn
        sar_message_dict['metadata']['tow'] = self.start_gst.tow
        sar_message_dict['metadata']['utc'] = self.start_gst.utc.strftime('%Y/%m/%d %H:%M:%S')
        sar_message_dict['metadata']['svid'] = f"{self.svid:02d}"
        sar_message_dict['rlm_id']['value'] = self.rlm_id.name
        sar_message_dict['rlm_id']['raw_value'] = self.rlm_id.value
        sar_message_dict['beacon_id']['raw_value'] = beacon_id.hex
        sar_message_dict['message_code']['value'] = message_code.name
        sar_message_dict['message_code']['raw_value'] = self.current_message[60:64].bin
        sar_message_dict['rlm_params']['raw_value'] = SRLM_params.bin

        sar_message_dict['beacon_id_parsing_subblock'] = parse_beacon_id(beacon_id)

        return sar_message_dict


parser = argparse.ArgumentParser(description='Parse the Galileo I/NAV message for E1-B to extract and parse the SAR information.')
parser.add_argument('in_file', nargs='?', default='24_hours.sbf')
parser.add_argument('out_file', nargs='?', default='sar_output.json')
parser.add_argument('-s', '--skip-test', action='store_true', help="don't show the Test Service messages")
parser.add_argument('-u', '--unknown-protocols', action='store_true', help="create different file with all the unknown protocols")
args = parser.parse_args()

if __name__ == '__main__':

    sbf_iterator = SBF(args.in_file)

    sar_manager_svid = [SARMessage(svid) for svid in range(37)]
    stored_sar_messages = []
    stored_unknown_protocol_sar_messages = []

    for sar_data in sbf_iterator:

        if not sar_data.is_nominal_page:
            continue

        sar_message = sar_manager_svid[sar_data.svid].new_sar_data(sar_data)

        if sar_message is not None:
            stored_sar_messages.append(sar_message)
            if args.skip_test and sar_message['message_code']['value'] == MESSAGE_CODES.TEST_SERVICE.name:
                continue
            if args.unknown_protocols and sar_message['beacon_id_parsing_subblock']['protocol_code']['value'] == 'Unknown':
                stored_unknown_protocol_sar_messages.append(sar_message)
            print_sar_message(sar_message)

    if args.unknown_protocols:
        filename = args.out_file[:args.out_file.rfind('.')] + '_unknown_protocols.json'
        json.dump(stored_unknown_protocol_sar_messages, open(filename, 'w'), indent=2)

    json.dump(stored_sar_messages, open(args.out_file, 'w'), indent=2)
