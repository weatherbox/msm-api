import redis
import sys
import os
from msm import MSM
import datetime

def msm_to_redis(file, redis):
    msm = MSM(file)
    
    msm.parse_section0()
    sec1 = msm.parse_section1()
    sec3, grid = msm.parse_section3()

    date = datetime.datetime(
        sec1['year'][0],        
        sec1['month'][0],        
        sec1['day'][0],
        sec1['hour'][0],
        sec1['minute'][0],
        sec1['second'][0]
    )
    print date
    redis.set("msm:ref_time", date.strftime('%Y%m%d%H%M'))

    while not msm.is_end_section():
        sec4, pdt = msm.parse_section4()
        sec5, drt, bin_RED = msm.parse_section5(True)
        msm.parse_section6() # not used
        sec7, data = msm.parse_section7()

        key = ':'.join([
            'msm',
            str(pdt['forecast_time'][0]),
            msm.level(
                pdt['first_fixed_surface_type'],
                pdt['first_fixed_surface_scale_factor'],
                pdt['first_fixed_surface_scale_value']),
            msm.parameter(
                pdt['parameter_category'],
                pdt['parameter_number'])
        ])

        print key
        redis.set(key + ':RED', bin_RED)
        redis.set(key + ':data', data)
    
def store_to_redis(dete):
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        password=os.environ.get('REDIS_PASS'))
    
    filetypes = [
        "Lsurf_FH00-15", "Lsurf_FH16-33", "Lsurf_FH34-39",
        "L-pall_FH00-15", "L-pall_FH18-33", "L-pall_FH36-39"
    ]

    for filetype in filetypes:
        filename = "msm/Z__C_RJTD_" + date + "00_MSM_GPV_Rjp_" + filetype + "_grib2.bin"
        msm_to_redis(filename, r)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        date = sys.argv[1]
        store_to_redis(date)

    else:
        now = datetime.datetime.utcnow()
        dh = now.hour % 3 + 3
        d = now - datetime.timedelta(hours=dh)
        date = d.strftime('%Y%m%d%H00')
        print date

        import download
        download.download(date)
        store_to_redis(date)

