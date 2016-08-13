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
    return jsonify({'message': 'It works!'})

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

if __name__ == '__main__':
    app.run()
