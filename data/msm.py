""" MSM

Parse MSM file

GRIB2 documentation: http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_doc.shtml

"""

import sys
import numpy as np


class MSM:
    def __init__(self, file):
        self.filename = file
        self.fileptr = open(file, 'rb')


    def parse(self):
        msm = {}

        msm['sec0'] = self.parse_section0()
        msm['sec1'] = self.parse_section1()
        msm['sec3'], msm['grid'] = self.parse_section3()
        msm['data'] = []

        while not self.is_end_section():
            sec4, pdt = self.parse_section4()
            sec5, drt = self.parse_section5()
            sec6 = self.parse_section6() # not used
            sec7, data = self.parse_section7()

            msm['data'].append({
                'sec4': sec4,
                'pdt':  pdt,
                'sec5': sec5,
                'drt':  drt,
                'sec7': sec7
            })

            print '-'.join([
                str(pdt['forecast_time'][0]),
                self.level(
                    pdt['first_fixed_surface_type'],
                    pdt['first_fixed_surface_scale_factor'],
                    pdt['first_fixed_surface_scale_value']),
                self.parameter(
                    pdt['parameter_category'],
                    pdt['parameter_number'])
            ])
   
        return msm


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

    def parse_section3(self):
        section3_dtype = np.dtype([
            ('length', '>u4'),
            ('section_number', 'u1'),
            ('grid_difinition', 'u1'),
            ('data_points', '>u4'),
            ('length_optional_list', 'u1'),
            ('interpretaion_optional_list', 'u1'),
            ('grid_definition_template', '>u2')
        ])

        grid_definition_template_3_0 = np.dtype([
            ('shape_of_the_earth', 'u1'),
            ('scale_factor_radius', 'u1'),
            ('scale_value_radius', '>u4'),
            ('scale_factor_major_axis', 'u1'),
            ('scale_value_major_axis', '>u4'),
            ('scale_factor_minor_axis', 'u1'),
            ('scale_value_minor_axis', '>u4'),
            ('ni', '>u4'),
            ('nj', '>u4'),
            ('basic_angle', '>u4'),
            ('subdivision_basic_angle', '>u4'),
            ('la1', '>u4'),
            ('lo1', '>u4'),
            ('resolution_and_flags', 'u1'),
            ('la2', '>u4'),
            ('lo2', '>u4'),
            ('di', '>u4'),
            ('dj', '>u4'),
            ('scanning_mode', 'u1')
        ])
        
        sec3 = np.fromfile(self.fileptr, dtype=section3_dtype, count=1)

        if sec3['grid_definition_template'] == 0: 
            return sec3, np.fromfile(self.fileptr, dtype=grid_definition_template_3_0, count=1)

        else:
            raise Exception('unknown grid definition template')


    def parse_section4(self):
        section4_dtype = np.dtype([
            ('length', '>u4'),
            ('section_number', 'u1'),
            ('coordinate_values_after_template', '>u2'),
            ('product_definition_template', '>u2')
        ])
        
        sec4 = np.fromfile(self.fileptr, dtype=section4_dtype, count=1)

        if sec4['product_definition_template'] == 0:
            return sec4, self.product_definition(0)
        
        elif sec4['product_definition_template'] == 8: 
            return sec4, self.product_definition(8)

        else:
            raise Exception('unknown product definition template')


    def product_definition(self, template):
        product_definition_template_4_0 = [
            ('parameter_category', 'u1'),
            ('parameter_number', 'u1'),
            ('generating_type', 'u1'),
            ('background_id', 'u1'),
            ('analysis_or_forecast', 'u1'),
            ('data_cutoff_hours', '>u2'),
            ('data_cutoff_minutes', 'u1'),
            ('indicator_time_range_unit', 'u1'),
            ('forecast_time', '>u4'),
            ('first_fixed_surface_type', 'u1'),
            ('first_fixed_surface_scale_factor', 'u1'),
            ('first_fixed_surface_scale_value', '>u4'),
            ('second_fixed_surface_type', 'u1'),
            ('second_fixed_surface_scale_factor', 'u1'),
            ('second_fixed_surface_scale_value', '>u4')
        ]

        product_definition_template_4_8 = product_definition_template_4_0 + [
            ('year', '>u2'),
            ('month', 'u1'),
            ('day', 'u1'),
            ('hour', 'u1'),
            ('minute', 'u1'),
            ('second', 'u1'),
            ('num_time_ranges_specifications', 'u1'),
            ('num_missing_data_values', '>u4'),
            ('statistical_process_type', 'u1'),
            ('statistical_time_increment_type', 'u1'),
            ('statistical_indicator_time_range_unit', 'u1'),
            ('statistical_time_range_length', '>u4'),
            ('indicator_incremant_time_unit', 'u1'),
            ('time_incremant', '>u4')  
        ]

        if template == 0:
            return np.fromfile(self.fileptr, dtype=np.dtype(product_definition_template_4_0), count=1)
        
        elif template == 8:
            return np.fromfile(self.fileptr, dtype=np.dtype(product_definition_template_4_8), count=1)


    def parse_section5(self):
        section5_dtype = np.dtype([
            ('length', '>u4'),
            ('section_number', 'u1'),
            ('num_data_points', '>u4'),
            ('data_representation_template', '>u2')
        ])

        # data representation tmeplate 5.0 - simple packing
        drt_5_0 = np.dtype([
            ('R', 'f4'),
            ('E', '>u2'),
            ('D', '>u2'),
            ('num_bits', 'u1'),
            ('original_field_type', 'u1')
        ])
        
        sec5 = np.fromfile(self.fileptr, dtype=section5_dtype, count=1)
        
        if sec5['data_representation_template'] == 0: 
            return sec5, np.fromfile(self.fileptr, dtype=drt_5_0, count=1)

        else:
            raise Exception('unknown data representation template')


    def parse_section6(self):
        section6_dtype = np.dtype([
            ('length', '>u4'),
            ('section_number', 'u1'),
            ('bitmap_indicator', 'u1')
        ])
        return np.fromfile(self.fileptr, dtype=section6_dtype, count=1)


    def parse_section7(self):
        section7_dtype = np.dtype([
            ('length', '>u4'),
            ('section_number', 'u1')
        ])

        sec7 = np.fromfile(self.fileptr, dtype=section7_dtype, count=1)
        data = self.fileptr.read(sec7['length'] - 5)

        return sec7, data


    def is_end_section(self):
        if self.fileptr.read(4) == "7777":
            return True

        else:
            self.fileptr.seek(-4, 1) # back to previous point
            return False

    def parameter(self, category, number):
        params = {
            0: {
                'category': 'Temperture',
                0: 'TMP'
            },
            1: {
                'category': 'Moisture',
                1: 'RH',
                8: 'APCP'
            },
            2: {
                'category': 'Momentum',
                2: 'UGRD',
                3: 'VGRD',
                8: 'VVEL'
            },
            3: {
                'category': 'Mass',
                0: 'PRES',
                1: 'PRMSL',
                5: 'HGT'
            },
            6: {
                'category': 'Cloud',
                1: 'TCDC',
                3: 'LCDC',
                4: 'MCDC',
                5: 'HCDC'
            }
        }
        return params[category[0]][number[0]]


    def level(self, type, scale_factor, scale_value):
        if type == 1:
            return 'Surface' # Ground or Water Surface

        elif type == 101:
            return 'Surface' # Mean Sea Level

        elif type == 103:
            return 'Surface' # Special Height Above Ground

        elif type == 100: # Isobaric Surface
            return str(scale_value[0])

        else:
            return


if __name__ == '__main__':
    file = sys.argv[1]
    msm = MSM(file)
    print msm.parse()

