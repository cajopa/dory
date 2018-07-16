#!/usr/bin/env python

import json
import random
import string

from flask import Flask, request, Response
import redis


class DoryApp(Flask):
    def __init__(self):
        super(DoryApp, self).__init__('dory')
        
        #TODO: load host, port, and db from confs
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        
        self.add_url_rule('/', 'receive_data', self.receive_data, methods=['POST'])
        self.add_url_rule('/<id_>', 'divulge_data', self.divulge_data, methods=['GET'])

    def receive_data(self):
        #TODO: take expiration time from confs
        while True: #loop handles collisions
            keyname = self.random_keyname()
            if self.redis_client.set(keyname, request.get_data(cache=False), ex=60, nx=True):
                break
        
        return Response(
            response=json.dumps({'url': keyname}),
            mimetype='application/json'
        )

    def divulge_data(self, id_=None):
        with self.redis_client.pipeline() as p:
            p.get(id_)
            p.delete(id_)
            to_return = p.execute()[0]
        
        if to_return:
            return self.make_response(to_return)
        else:
            return Response(status=404)
    
    @classmethod
    def random_keyname(cls):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(32))


if __name__=='__main__':
    DoryApp().run(host='0.0.0.0', port=5001)
