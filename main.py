#!/usr/bin/env python

import json
import random
import string

from flask import Flask, request, Response, abort
import redis


app = Flask('dory')

#TODO: load host, port, and db from confs
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


@app.route('/', methods=['POST'])
def receive_data():
    #TODO: take expiration time from confs
    while True: #loop handles collisions
        keyname = random_keyname()
        if redis_client.set(keyname, request.get_data(cache=False), ex=60, nx=True):
            break
    
    return Response(
        response=json.dumps({'url': keyname}),
        mimetype='application/json'
    )

@app.route('/<id_>', methods=['GET'])
def divulge_data(id_=None):
    with redis_client.pipeline() as p:
        p.get(id_)
        p.delete(id_)
        to_return = p.execute()[0]
    
    if to_return:
        return app.make_response(to_return)
    else:
        abort(404)

def random_keyname():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(32))


if __name__=='__main__':
    app.run(host='0.0.0.0', port=5001)
