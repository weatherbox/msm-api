import math

def get_wind_dir(u, v):
    wdir = math.pi / 2 - math.atan2(-v, -u)
    if wdir < 0: wdir += 2 * math.pi
    return math.degrees(wdir)

def get_wind_speed(u, v):
    return math.sqrt(u * u + v * v)

def get_wind_dir_speed(u, v):
    return get_wind_dir(u, v), get_wind_speed(u,v)


def celsius(k):
    return k - 273.15


