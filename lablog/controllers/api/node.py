from flask import Blueprint, Response, render_template, request, g, abort, current_app, session
from flask.views import MethodView
from lablog.app import App
from lablog import config
from lablog.util.jsontools import jsonify
from lablog import messages
from lablog.interfaces.sensornode import Node
from flask_oauthlib.provider import OAuth2Provider
from lablog.controllers.auth import oauth
from datetime import datetime
import logging
import json

node = Blueprint(
    'node',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/api/{}/node".format(config.API_VERSION),
)

k = list(config.SKEY)
k.append(0x00)
SKEY = bytearray(k)
KEY = buffer(SKEY)

@node.route("/nodes", methods=["GET"])
@oauth.require_oauth('analytics')
def get_nodes():
    res = g.INFLUX.query(query="SHOW SERIES FROM \"node.light\"")
    nodes = []
    for v in res.get_points():
        nodes.append(v.get('node'))
    return jsonify({"nodes":nodes})

@node.route("/<node_id>/sensors", methods=["POST"])
def node_sensors(node_id):
    n = Node.find_one({'id':node_id})
    n.go(g.INFLUX, g.MQ, data=request.data)
    n._last_run = datetime.utcnow()
    n.save()
    return jsonify({'success':True})

@node.route("/<node_id>/sensors", methods=["GET"])
@oauth.require_oauth('analytics')
def get_node_sensors(node_id):
    q = "SELECT value FROM \"lablog\".\"15minute\"./node.*/ WHERE time > now() - 2d AND node='{}'".format(node_id)
    res = g.INFLUX.query(q)
    ret = {}
    logging.info(res.raw)
    for k, v in res.items():
        ret[k[0]] = []
        for i in v:
            ret[k[0]].append(i)

    return jsonify(ret)
