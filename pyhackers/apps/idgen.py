

from flask import request, jsonify, Blueprint
from pyhackers.idgen import IdGenerator, StatsHandler, idgen_client
from pyhackers.config import config

url_prefix = config.get("idgen", "url_prefix")

idgen_app = Blueprint('idgen_service', __name__, url_prefix=url_prefix)

# idgenerator = IDGen()
stats_handler = StatsHandler()


@idgen_app.route("/new", methods=['GET'])
def generate():
    return str(idgen_client.get())


@idgen_app.route("/flush", methods=['GET'])
def flush():
    return jsonify(stats_handler.get(flush=True))


@idgen_app.route("/stats", methods=['GET'])
def stats():
    return jsonify(stats_handler.get())
