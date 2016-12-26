import math
import struct
import datetime

class MsmRedis:
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

    def __init__(self, redis):
        self.redis = redis


    def get_ref_time(self):
        return self.redis.get('msm:ref_time')

    def key(self, ft, level, element):
        return ':'.join(['msm', str(ft), level, element])


    def get(self, ft, level, element, lat, lon):
        n = self.calculate_grid(level, lat, lon)
        key = self.key(ft, level, element)
        return self.get_from_redis(key, n)


    # get many elements using pipeline
    # elements is list of [ft, level, element, lat, lon]
    def get_pipe(self, elements):
        pipe = self.redis.pipeline(transaction=False)
        pipe.get('msm:ref_time')
        keys = []
        ns = [] # use unpacking

        for elem in elements:
            n = self.calculate_grid(elem[1], elem[3], elem[4])
            key = self.key(elem[0], elem[1], elem[2])
            nbyte = int(math.floor(n * self.nbit / 8))

            keys.append(key)
            ns.append(n)
            packing_RED = pipe.get(key + ':RED')
            data = pipe.getrange(key + ':data', nbyte, nbyte + 1)

        values = pipe.execute()
        ref_time = values[0]
        res = {}

        for i, n in enumerate(ns):
            RED  = values[2*i + 1]
            data = values[2*i + 2]
            res[keys[i]] = self.decode_data(data, RED, n)

        return ref_time, res


    def calculate_grid(self, level, lat, lon):
        grid = self.surf if level == 'surface' else self.pall

        # bounds check
        if lat > self.la1 or lat < self.la2 or lon < self.lo1 or lon > self.lo2:
            return None

        # calculate grid pos
        x = math.floor((lon - self.lo1) / grid['dx'])
        y = math.floor((self.la1 - lat) / grid['dy']) 
        n = y * grid['nx'] + x
        return n


    def get_from_redis(self, key, n):
        RED = self.redis.get(key + ':RED')
        nbyte = int(math.floor(n * self.nbit / 8))
        data = self.redis.getrange(key + ':data', nbyte, nbyte + 1) # get 16bit data
        return self.decode_data(data, RED, n)


    def decode_data(self, data, RED, n):
        if not(data and RED):
            return None

        # 16bit -> 12bit
        value = struct.unpack('>H', data)[0]
        if n % 2 == 0:
            value = value >> 4
        else:
            value = value & 0b0000111111111111

        return self.unpack_simple(value, RED)


    def unpack_simple(self, x, packing_RED):
        d = struct.unpack('>f 2H', packing_RED)
        x = float(x)
        R = d[0]
        E = float(self.neg16(d[1]))
        D = float(self.neg16(d[2]))

        return (R + x * math.pow(2, E)) / math.pow(10, D)


    # first bit indicates negative number
    def neg16(self, x):
        if x & 0b1000000000000000 > 0:
            x = (x & 0b0111111111111111) * -1
        return x



if __name__ == '__main__':
    import redis
    import os
    redis = redis.Redis(
        host=os.environ.get('REDIS_HOST'),
        password=os.environ.get('REDIS_PASS'))
    msm = MsmRedis(redis)

    print msm.get('0', 'surface', 'TMP', 35, 135)
    print msm.get('0', 'surface', 'PRMSL', 35, 135)
    print msm.get('0', 'surface', 'TMP', 40, 135)
    print msm.get('0', '100', 'TMP', 35, 135)

