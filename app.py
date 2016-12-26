from chalice import Chalice

import os
import redis

from chalicelib import msm_redis
from chalicelib import units

app = Chalice(app_name='msm-api')
app.debug = True

redis = redis.Redis(
    host=os.environ.get('REDIS_HOST'),
    password=os.environ.get('REDIS_PASS'))
msm = msm_redis.MsmRedis(redis)


@app.route('/', cors=True)
def index():
    return {'message': 'Welcome to msm-api! See the api document http://docs.msmapi.apiary.io/'}

@app.route('/data/{ref_time}/{ft}/{level}/{element}/{lat}/{lon}', cors=True)
def data(ref_time, ft, level, element, lat, lon):
    ref_time = msm.get_ref_time()
    value = msm.get(ft, level, element, float(lat), float(lon))
    return {
        'ref_time': ref_time,
        'ft': ft,
        'level': level,
        'element': element,
        'value': value
    }

@app.route('/sounding/{ref_time}/{ft}/{lat}/{lon}', cors=True)
def sounding(ref_time, ft, lat, lon):
    elements = []
    levels = {}
    lat, lon = float(lat), float(lon)

    # surface
    levels['surface'] = {}
    for e in ['TMP', 'RH', 'UGRD', 'VGRD', 'PRES']:
        elements.append([ft, 'surface', e, lat, lon])

    # 1000 - 300
    mid = ['1000', '975', '950', '925', '900', '850']
    mid += [str(x) for x in range(800, 299, -100)]
    for level in mid:
        levels[level] = {}
        for e in ['TMP', 'RH', 'UGRD', 'VGRD', 'HGT']:
            elements.append([ft, level, e, lat, lon])

    # 250 - 100
    for level in [str(x) for x in range(250, 99, -50)]:
        levels[level] = {}
        for e in ['TMP', 'UGRD', 'VGRD', 'HGT']:
            elements.append([ft, level, e, lat, lon])

    # get from redis pipeline
    ref_time, values = msm.get_pipe(elements)

    for i,v in enumerate(values.values()):
        e = elements[i]
        levels[e[1]][e[2]] = v

    return {
        'ref_time': ref_time,
        'ft': ft,
        'levels': levels
    }


@app.route('/sky/{ref_time}/{lat}/{lon}', cors=True)
def sky(ref_time, lat, lon):
    elements = []
    lat, lon = float(lat), float(lon)
    upper_levels = ['1000', '975', '950', '900', '850']

    # upper wind
    for ft in range(0, 40, 3):
        for l in upper_levels:
            elements.append([ft, l, 'UGRD', lat, lon])
            elements.append([ft, l, 'VGRD', lat, lon])

    # surface
    for ft in range(0, 40):
        for e in ['UGRD', 'VGRD', 'TMP', 'PRES', 'APCP', 'LCDC', 'MCDC', 'HCDC']:
            elements.append([ft, 'surface', e, lat, lon])

    ref_time, values = msm.get_pipe(elements)

    upper_wind = []
    for ft in range(0, 40, 3):
        winds = { 'ft': ft }

        for l in upper_levels:
            u = values[msm.key(ft, l, 'UGRD')]
            v = values[msm.key(ft, l, 'VGRD')]
            wdir, speed = units.get_wind_dir_speed(u, v)
            winds[l] = { 'from': wdir, 'speed': speed }

        upper_wind.append(winds)

    surface = []
    for ft in range(0, 40):
        u = values[msm.key(ft, 'surface', 'UGRD')]
        v = values[msm.key(ft, 'surface', 'VGRD')]
        wdir, speed = units.get_wind_dir_speed(u, v)

        surface.append({
            'ft': ft,
            'wind': { 'from': wdir, 'speed': speed },
            'temp': units.celsius(values[msm.key(ft, 'surface', 'TMP')]),
            'pressure': values[msm.key(ft, 'surface', 'PRES')] / 100,
            'rain':     values[msm.key(ft, 'surface', 'APCP')],
            'clouds': {
                'low':    values[msm.key(ft, 'surface', 'LCDC')],
                'middle': values[msm.key(ft, 'surface', 'MCDC')],
                'high':   values[msm.key(ft, 'surface', 'HCDC')]
            }
        })


    return {
        'ref_time': ref_time,
        'upper_wind': upper_wind,
        'surface': surface
    }

