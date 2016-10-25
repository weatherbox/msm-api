from flask import Flask, jsonify
import os
import redis
from data import msm_redis

app = Flask(__name__)

redis = redis.Redis(
    host=os.environ.get('REDIS_HOST'),
    password=os.environ.get('REDIS_PASS'))
msm = msm_redis.MsmRedis(redis)

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to msm-api! See the api document http://docs.msmapi.apiary.io/'})

@app.route('/data/<ref_time>/<ft>/<level>/<element>/<float:lat>/<float:lon>')
def data(ref_time, ft, level, element, lat, lon):
    ref_time = msm.get_ref_time()
    value = msm.get(ft, level, element, lat, lon)
    res = {
        'ref_time': ref_time,
        'ft': ft,
        'level': level,
        'element': element,
        'value': value
    }
    return jsonify(res)

@app.route('/sounding/<ref_time>/<ft>/<float:lat>/<float:lon>')
def sounding(ref_time, ft, lat, lon):
    elements = []
    levels = {}

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

    for i,v in enumerate(values):
        e = elements[i]
        levels[e[1]][e[2]] = v

    res = {
        'ref_time': ref_time,
        'ft': ft,
        'levels': levels
    }
    return jsonify(res)


if __name__ == '__main__':
    app.debug = True
    app.run()

