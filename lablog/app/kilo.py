from geventwebsocket import WebSocketApplication
from lablog import config
from lablog import db
from lablog.util.jsontools import JavascriptEncoder
from lablog.models.client import Token, Admin
from uuid import uuid4
from datetime import datetime
import humongolus
import gevent
import logging
import urlparse
import json
import os

logging.basicConfig(level=config.LOG_LEVEL)

class SocketException(Exception):

    def json(self):
        return {
            'message':self.message
        }

def verify_message(client, scopes):
    args = urlparse.parse_qs(client.environ.get('QUERY_STRING'))
    token = args.get('token')[0]
    client_id = args.get('client_id')[0]
    t = Token.find_one({'refresh_token':token})
    if str(t._get('client')._value) == client_id and t.expires > datetime.utcnow():
        for i in scopes:
            if not i in t.scopes: raise SocketException('Invalid scope')
        return t
    else:
        raise SocketException("Invalid Token")

class Kilo(WebSocketApplication):

    def __init__(self, *args, **kwargs):
        super(Kilo, self).__init__(*args, **kwargs)
        MONGO = db.init_mongodb()
        humongolus.settings(logging, MONGO)

    @classmethod
    def protocol_name(cls):
        return "json"

    def on_open(self):
        token = verify_message(self.ws.handler.active_client.ws, ['inoffice'])
        self.name = 'foo'
        current = self.ws.handler.active_client
        current.token = token
        ev = {'event':'me', '_to':current.address, 'data':{'room':self.name}}
        self.sendto(ev)
        ev['event'] = 'joined'
        self.broadcast(ev)

    def on_message(self, ms):
        try:
            token = self.ws.handler.active_client.token
            ms = json.loads(ms)
            ms['token'] = token
            ev = ms['event']
            ms['_to'] = tuple(ms.get('_to', {}))
            actions = {
                'inoffice': self.inoffice,
                'beacons': self.beacons,
                'ping': self.ping,
            }
            actions[ev](ms)
        except SocketException as e:
            logging.exception(e)
            self.ws.handler.active_client.ws.send(json.dumps({'event':'invalid_access',  'data':e.json()}))
        except Exception as e:
            logging.exception(e)

    def ping(self, data):
        logging.info(u"{} pinged...".format(data['token'].user.name))

    def beacons(self, data):
        #TODO write beacon data to data store
        #logging.info(data['data']['result']['beacons'])
        pass

    def inoffice(self, data):
        logging.info(data['data']['result'])
        user = data['token'].user
        user.in_office = data['data']['result']
        user.save();
        data['data']['user'] = user.json()
        self.broadcast(data)

    def on_close(self, reason):
        current = self.ws.handler.active_client
        logging.info("Client Left: {}".format(current.address))
        ev = {'event':'bye', 'data':{'room':self.name}}
        self.broadcast(ev)

    def sendto(self, ms):
        _to = self.ws.handler.server.clients.get(ms['_to'])
        if _to: _to.ws.send(json.dumps(ms, cls=JavascriptEncoder))

    def broadcast(self, message):
        for client in self.ws.handler.server.clients.values():
            try:
                client.ws.send(json.dumps(message, cls=JavascriptEncoder))
            except Exception as e:
                logging.error(e)
