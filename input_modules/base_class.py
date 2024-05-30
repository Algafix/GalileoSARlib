from bitstring import BitArray

from aux.aux_classes import RLM, GST

class SARFormat:

    def __init__(self, svid, wn, tow, full_page) -> None:

        self.page_bits: BitArray = full_page
        self.svid: int = svid
        self.gst = GST(wn=wn, tow=tow)

        self.is_nominal_page = not (self.is_dummy_page or self.is_alert_page)
        if self.is_nominal_page:
            self.start_bit = full_page[178]
            self.rlm_id = RLM(full_page[179])
            self.rlm_data = full_page[180:200]

    @property
    def is_dummy_page(self) -> bool:
        return self.page_bits[2:8].uint == 63

    @property
    def is_alert_page(self) -> bool:
        return self.page_bits[1] 

class PageIterator:
    """
    Abstract class to be implemented by any input format
    """
    def __init__(self):
        pass

    def __iter__(self) -> 'PageIterator':
        return self

    def __next__(self) -> 'SARFormat':
        pass
