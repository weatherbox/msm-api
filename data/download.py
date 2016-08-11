import sys
import os

date = sys.argv[1]
source = "http://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/original/"

if len(date) != 12:
    print "invalid date"
    sys.exit()

filetypes = [
    "Lsurf_FH00-15", "Lsurf_FH16-33", "Lsurf_FH34-39",
    "L-pall_FH00-15", "L-pall_FH18-33", "L-pall_FH36-39"
]

for filetype in filetypes:
    filename = "Z__C_RJTD_" + date + "00_MSM_GPV_Rjp_" + filetype + "_grib2.bin"
    url = source + "/".join([date[0:4], date[4:6], date[6:8], filename])
    os.system("wget " + url)

