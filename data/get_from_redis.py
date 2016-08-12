import math
import struct
import datetime

# grid definitions
nbit = 12
la1 = 47.6
lo1 = 120.0
la2 = 22.4
lo2 = 150.0
surf = {
    'dx': 0.0625,
    'dy': 0.05,
    'nx': 481,
    'ny': 505
}
pall = {
    'dx': 0.125,
    'dy': 0.1,
    'nx': 241,
    'ny': 253
}


def get(ft, level, element, lat, lon, redis):
    grid = surf if level == 'Surface' else pall

    # bounds check
    if lat > la1 or lat < la2 or lon < lo1 or lon > lo2:
        return

    x = math.floor((lon - lo1) / grid['dx'])
    y = math.floor((la1 - lat) / grid['dy']) 
    n = y * grid['nx'] + x
    nbyte = int(math.floor(n * nbit / 8))

    key = ':'.join(['msm', ft, level, element])
    packing_RED = redis.get(key + ':RED')
    data = redis.getrange(key + ':data', nbyte, nbyte + 1) # get 16bit data
    value = struct.unpack('>H', data)[0]

    if not(data and packing_RED):
        return None

    # 16bit -> 12bit
    if n % 2 == 0:
        value = value >> 4
    else:
        value = value & 0b0000111111111111

    return unpack_simple(value, packing_RED)


def unpack_simple(x, packing_RED):
    d = struct.unpack('>f 2H', packing_RED)
    x = float(neg12(x))
    R = d[0]
    E = float(neg16(d[1]))
    D = float(neg16(d[2]))

    return (R + x * math.pow(2, E)) / math.pow(10, D)


def neg12(x):
    if x & 0b100000000000 > 0:
        x = (x & 0b011111111111) * -1
    return x

def neg16(x):
    if x & 0b1000000000000000 > 0:
        x = (x & 0b0111111111111111) * -1
    return x



if __name__ == '__main__':
    import redis
    redis = redis.Redis(host='192.168.33.11')

    print get('0', 'Surface', 'TMP', 35, 135, redis)
    print get('0', 'Surface', 'TMP', 40, 135, redis)
    print get('0', '100', 'TMP', 35, 135, redis)

