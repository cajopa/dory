import json
import random
import string

import cherrypy
import redis


@cherrypy.expose
class Main(object):
    #TODO: load host, port, and db from confs
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    
    
    def POST(self, data):
        #TODO: take expiration time from confs
        filename = self.random_filename()
        redis_client.set(filename, data, ex=60, nx=True)
        
        #TODO: automatic dumpsing how?
        return json.dumps({'url': filename})
    
    ################################
    
    @classmethod
    def random_filename(cls):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(32))


if __name__=='__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')]
        }
    }
    
    cherrypy.quickstart(Main())
