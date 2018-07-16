#!/usr/bin/env python

import os
import random
import string

from flask import Flask, request, Response, jsonify
import redis


class DoryApp(Flask):
    def __init__(self):
        super(DoryApp, self).__init__('dory')
        
        self.config.update(
            REDIS_HOST='localhost',
            REDIS_PORT=6379,
            REDIS_DB=0,
            
            SERVER_NAME = '0.0.0.0:5001'
        )
        
        self.config.from_json(os.environ.get('DORY_CONF', 'dory.conf'))
        
        #TODO: load host, port, and db from confs
        self.redis_client = redis.StrictRedis(
            host=self.config['REDIS_HOST'],
            port=self.config['REDIS_PORT'],
            db=self.config['REDIS_DB']
        )
        
        self.add_url_rule('/', 'receive_data', self.receive_data, methods=['POST'])
        self.add_url_rule('/<id_>', 'divulge_data', self.divulge_data, methods=['GET'])

    def receive_data(self):
        #TODO: take expiration time from confs
        while True: #loop handles collisions
            keyname = self.random_keyname()
            if self.redis_client.set(keyname, request.get_data(cache=False), ex=60, nx=True):
                break
        
        return jsonify({'url': keyname})

    def divulge_data(self, id_=None):
        with self.redis_client.pipeline() as p:
            p.get(id_)
            p.delete(id_)
            to_return = p.execute()[0]
        
        if to_return:
            return Response(response=to_return, mimetype='application/octet-stream')
        else:
            return Response(status=404)
    
    @classmethod
    def random_keyname(cls):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(32))


if __name__=='__main__':
    DoryApp().run()
