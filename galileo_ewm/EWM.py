from datetime import datetime, timedelta
from bitstring import BitArray

from aux.EWM_aux import *

class EWM:

    MESSAGE_ID_SLICE = slice(0,16)
    HAZARD_SLICE = slice(16, 25)
    CHRONOLOGY_SLICE = slice(25, 42)
    GUIDANCE_SLICE = slice(42, 56)
    AREA_SLICE = slice(56, 105)
    ADDITIONAL_SLICE = slice(105, 122)

    def __init__(self, ewm_bits: str, wn: int):
        print(ewm_bits)
        self.sar_wn = wn
        self.sar_bits = ewm_bits
        self.alert_id = self._create_alert_id(ewm_bits)

        self.message_type = None
        self.country = None
        self.provider = None
        self._parse_message_id(ewm_bits[EWM.MESSAGE_ID_SLICE])
        
        self.hazard = None
        self.severity = None
        self._parse_hazard(ewm_bits[EWM.HAZARD_SLICE])

        self.hazard_time: datetime = None
        self.duration = None
        self._parse_chronology(ewm_bits[EWM.CHRONOLOGY_SLICE])

        self.library = None
        self.lib_version = None
        self.guidande_A = None
        self.guidande_B = None
        self._parse_guidance(ewm_bits[EWM.GUIDANCE_SLICE])

        self.centre_lat = None
        self.centre_lon = None
        self.smajor = None
        self.sminor = None
        self.az_angle = None

        self.subj_settings = None
        self.settings = None

    def _parse_message_id(self, message_id: str):
        self.message_type = MessageType(message_id[0:2])
        self.country = CountryRegion(message_id[2:11])
        self.provider = ProviderId(message_id[11:16])

    def _parse_hazard(self, hazard: str):
        self.hazard = Hazard(hazard[0:7])
        self.severity = Severity(hazard[7:9])

    def _parse_chronology(self, chronology: str):
        hazard_wn = self.sar_wn + int(chronology[0])
        hazard_tow_field = int(chronology[1:15], base=2)
        self.duration = HazardDuration(chronology[15:17])
        if not (0 != hazard_tow_field < 10081):
            raise ValueError(f"Hazard ToW invalid! {hazard_tow_field}")
        hazard_tow = (hazard_tow_field-1) * 60  # field starts at 1 and to seconds
        self.hazard_time = datetime(1980,1,7) + timedelta(weeks=hazard_wn, seconds=hazard_tow)
        
    def _parse_guidance(self, guidance: str):
        self.library = LibrarySelection(guidance[0])
        self.lib_version = int(guidance[1:4], base=2)
        self.guidande_A = InternationalLibraryA(guidance[4:9])
        self.guidande_B = InternationalLibraryB(guidance[9:14])

    def _parse_area(self, area: str):
        pass

    def _parse_additional(self, additional: str):
        pass

    def _create_alert_id(self, ewm_bits):
        all_bits = BitArray(bin=ewm_bits[2:23]) + BitArray(bin=ewm_bits[25:40])
        return all_bits.hex


    def __str__(self):
        message_info = f"{self.message_type} - From {self.country} - Authority {self.provider}"
        hazard_info = f"Hazard type {self.hazard} of severity {self.severity}"
        chronology_info = f"Alert starting on {self.hazard_time} with a duration {self.duration}"
        guidance_info = f"Population instructions: {self.library.label} v. {self.lib_version}.\n{self.guidande_A.label} {self.guidande_B.label}"
        area_info = f"Affected area: TBC"
        additional_info = f"Additional info: TBC"

        return f"{message_info}\n{hazard_info}\n{chronology_info}\n{guidance_info}\n{area_info}\n{additional_info}\n"


if __name__ == "__main__":
    
    msg = CountryRegion('111')

    print(msg)
    print(msg.label)

