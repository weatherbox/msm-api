import sys
import os

date = sys.argv[1]
source = "http://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/original/"

if (len(date) != 12):
    print "invalid date"
    sys.exit()

for level in ["Lsurf", "L-pall"]:
    for ft in ["00-15", "16-33", "34-39"]:
        filename = "Z__C_RJTD_" + date + "00_MSM_GPV_Rjp_" + level + "_FH" + ft + "_grib2.bin"
        url = source + "/".join([date[0:4], date[4:6], date[6:8], filename])
        os.system("wget " + url)

