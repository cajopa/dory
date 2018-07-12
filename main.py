import json
import random
import string

from flask import Flask
import redis


app = Flask(__name__)

#TODO: load host, port, and db from confs
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


@app.route('/', methods=['POST'])
def receive_data(data):
    #TODO: take expiration time from confs
    filename = self.random_filename()
    redis_client.set(filename, data, ex=60, nx=True)
    
    #TODO: automatic dumpsing how?
    return json.dumps({'url': filename})

@app.route('/<id_>', methods=['GET'])
def divulge_data(id_=None):
    to_return = app.make_response(redis_client.get(id_))
    redis_client.expire(id_, 0)
    return to_return

def random_filename():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(32))


if __name__=='__main__':
    app.run()
