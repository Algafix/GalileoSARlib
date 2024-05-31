from enum import IntEnum, Enum
from typing import Union
from datetime import datetime, timedelta

from bitstring import BitArray


class RLM(IntEnum):
    SHORT_RLM = 0
    LONG_RLM = 1

class MESSAGE_CODES(Enum):
    ACK_SERVICE     = '0001'
    TEST_SERVICE    = '1111'
    SPARE           = 'spare'
    @classmethod
    def _missing_(cls, value):
        return cls.SPARE


LEN_GST = 32
LEN_WN = 12
LEN_TOW = 20

WN_MODULO = 4096
MAX_TOW = 604799
MIN_TOW = 0


class GST:

    def __init__(self, *args, **kwargs):
        self.initialized = True
        if len(args) == 0 and len(kwargs) == 0:
            self.initialized = False
            self.wn = None
            self.tow = None
        elif len(args) > 0:
            gst = args[0]
            self.wn = gst[:LEN_WN].uint
            self.tow = gst[LEN_WN:].uint
        else:
            self.wn = kwargs.get('wn', 0)
            self.tow = kwargs.get('tow', 0)

            if self.tow < 0:
                q, r = divmod(self.tow, MAX_TOW+1)
                self.wn += q
                self.tow = r

    def __str__(self):
        return f"{self.wn} {self.tow}"

    ### Logical operators ###

    def __bool__(self):
        return self.initialized

    def __eq__(self, other: Union['GST', BitArray, int]):

        if not self.initialized and not other.initialized:
            return True
        elif self.initialized ^ other.initialized:
            return False

        if isinstance(other, int):
            other = GST(tow=other)
        return self.int == other.int

    def __lt__(self, other: Union['GST', BitArray, int]):
        if isinstance(other, int):
            other = GST(tow=other)
        return self.int < other.int

    def __le__(self, other: Union['GST', BitArray, int]):
        if isinstance(other, int):
            other = GST(tow=other)
        return self.int <= other.int

    def __gt__(self, other: Union['GST', BitArray, int]):
        if isinstance(other, int):
            other = GST(tow=other)
        return self.int > other.int

    def __ge__(self, other: Union['GST', BitArray, int]):
        if isinstance(other, int):
            other = GST(tow=other)
        return self.int >= other.int

    ### Addition ###

    def __add__(self, other: Union[int, 'GST']) -> 'GST':
        if isinstance(other, int):
            tow = self.tow + other
            wn = self.wn
        elif isinstance(other, GST):
            tow = self.tow + other.tow
            wn = self.wn + other.wn
        else:
            raise TypeError(f"Type {type(other)} not supported for addition.")

        if tow > MAX_TOW:
            q, r = divmod(tow, MAX_TOW+1)
            wn += q
            tow = r

        return GST(tow=tow, wn=wn)

    ### Subtraction ###

    def __sub__(self, other: Union[int, 'GST']) -> 'GST':
        if isinstance(other, int):
            tow = self.tow - other
            wn = self.wn
        elif isinstance(other, GST):
            tow = self.tow - other.tow
            wn = self.wn - other.wn
        else:
            raise TypeError(f"Type {type(other)} not supported for subtraction.")

        if tow < MIN_TOW:
            q, r = divmod(tow, MAX_TOW+1)
            wn += q
            tow = r

        return GST(tow=tow, wn=wn)

    def __floordiv__(self, other: int) -> int:
        return self.total_seconds // other

    def __mod__(self, other: int) -> int:
        return self.tow % other

    ### Accessors ###

    @property
    def bitarray(self):
        return BitArray(uint=self.wn << LEN_TOW | self.tow, length=LEN_GST)

    @property
    def tow_bitarray(self):
        return BitArray(uint=self.tow, length=LEN_TOW)

    @property
    def wn_bitarray(self):
        return BitArray(uint=self.wn, length=LEN_WN)

    @property
    def int(self):
        return self.wn << LEN_TOW | self.tow

    @property
    def total_seconds(self):
        return (self.wn * (MAX_TOW+1)) + self.tow
    
    @property
    def utc(self) -> datetime:
        GPS_START = datetime(1980,1,6)
        UTC_LEAP_SECONDS = 18
        utc_time = GPS_START + timedelta(weeks=self.wn, seconds=self.tow-UTC_LEAP_SECONDS)
        return utc_time

