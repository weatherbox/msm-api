import sys
from io import BytesIO
import struct
import numpy as np


class MSM:
    def __init__(self, file):
        self.filename = file
        self.fileptr = open(file, 'rb')

        sec0 = self.parse_section0()
        sec1 = self.parse_section1()

        print sec0
        print sec1

    def parse_section0(self):
        section0_dtype = np.dtype([
            ('grib', 'S4'),
            ('reserved', 'S2'),
            ('discipline', 'u1'),
            ('edition', 'u1'),
            ('total_length', '>u8')
        ])
        return np.fromfile(self.fileptr, dtype=section0_dtype, count=1)

    def parse_section1(self):
        section1_dtype = np.dtype([
            ('length', '>u4'),
            ('section_number', 'u1'),
            ('originationg_center', '>u2'),
            ('originationg_subcenter', '>u2'),
            ('master_table_version', 'u1'),
            ('local_table_version', 'u1'),
            ('significance_reference_time', 'u1'),
            ('year', '>u2'),
            ('month', 'u1'),
            ('day', 'u1'),
            ('hour', 'u1'),
            ('minute', 'u1'),
            ('second', 'u1'),
            ('production_status', 'u1'),
            ('data_type', 'u1')
        ])
        return np.fromfile(self.fileptr, dtype=section1_dtype, count=1)


if __name__ == '__main__':
    file = sys.argv[1]
    msm = MSM(file)

