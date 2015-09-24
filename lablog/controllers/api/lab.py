from flask import Blueprint, Response, render_template, request, g
from flask.views import MethodView
from lablog.app import App
from lablog import config
from lablog.util.jsontools import jsonify
from flask_oauthlib.provider import OAuth2Provider
import logging
from lablog.controllers.auth import oauth

lab = Blueprint(
    'lab',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/api/{}/lab".format(config.API_VERSION),
)

@lab.route("/me", methods=["GET"])
@oauth.require_oauth('inoffice')
def me():
    me = request.oauth.user.json()
    me['times'] = request.oauth.user.get_punchcard(g.INFLUX)
    return jsonify(me)

@lab.route("/team", methods=["GET"])
@oauth.require_oauth('inoffice')
def team():
    ret = []
    for user in request.oauth.client.users():
        u = user.json()
        u['times'] = user.get_punchcard(g.INFLUX)
        ret.append(u)

    return jsonify(ret)

@lab.route("/ups", methods=["GET"])
@oauth.require_oauth('analytics')
def ups():
    q = "SELECT mean(\"value\") as value FROM \"lablog\"..ups_output_power WHERE time > now() - 12h GROUP BY time(15m), \"line\" fill(0)"
    res = g.INFLUX.query(q)
    ret = {}
    for s in res.raw['series']:
        n = "line-{}".format(s['tags']['line'])
        ret[n] = s['values']

    logging.info(ret)

    return jsonify(ret)

@lab.route("/energy", methods=["GET"])
@oauth.require_oauth('analytics')
def energy():
    q = "SELECT mean(\"power\") as value FROM \"lablog\"..smartmeter WHERE time > now() - 12h GROUP BY time(15m) fill(0)"
    res = g.INFLUX.query(q)
    ret = {}
    for k, v in res.items():
        ret[k[0]] = []
        for i in v:
            ret[k[0]].append(i)

    return jsonify(ret)

@lab.route("/weather", methods=["GET"])
@oauth.require_oauth('analytics')
def weather():
    q = "SELECT mean(\"value\") as value FROM \"lablog\"..\"temp-c\",\"relative-humidity\" WHERE time > now() - 12h GROUP BY time(15m) fill(0)"
    res = g.INFLUX.query(q)
    ret = {}
    for k, v in res.items():
        ret[k[0]] = []
        for i in v:
            ret[k[0]].append(i)

    return jsonify(ret)