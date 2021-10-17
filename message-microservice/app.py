from flask import Flask, Response, request
from flask_cors import CORS
import json
import logging
from datetime import datetime

import utils.rest_utils as rest_utils


from application_services.imdb_artists_resource import IMDBArtistResource
from application_services.MessageResource.message_service import MessageService
from application_services.UsersResource.user_service import UserResource
from database_services.RDBService import RDBService as RDBService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

##################################################################################################################

# DFF TODO A real service would have more robust health check methods.
# This path simply echoes to check that the app is working.
# The path is /health and the only method is GETs
@app.route("/health", methods=["GET"])
def health_check():
    rsp_data = {"status": "healthy", "time": str(datetime.now())}
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="app/json")
    return rsp


# The method take any REST request, and produces a response indicating what
# the parameters, headers, etc. are. This is simply for education purposes.

# Return all messages associated with a given conversation/inbox
@app.route("/api/message/inbox/<inbox>", methods=["GET", "POST", "DELETE"])
def get_conversation(inbox=None):
    """
    Returns a JSON object containing a description of the received request.

    :param inbox: inbox ID
    :return: JSON document containing information about the request.
    """

    # TODO -- We should wrap with an exception pattern.

    # Mostly for isolation. The rest of the method is isolated from the specifics of Flask.
    inputs = rest_utils.RESTContext(request, {"inbox": inbox})

    r_json = inputs.to_json()
    msg = {
        "/get_conversation received the following inputs": inputs.to_json()
    }
    logger.log("/api/message/inbox/<inbox> received/returned:\n", msg)

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp


# Return all conversation in the inbox for a given user
@app.route("/api/message/<user>", methods=["GET"])
def get_inbox(user):

    # logger.log("/api/event-participant/ received/returned:\n", res.to_json())
    # rsp = Response(json.dumps(res), status=200, content_type="application/json")

    res = MessageService.get_inbox_for_user(user)
    print("[app.get_inbox] returned: ", res)
    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp

@app.route('/hello')
def hello_world():
    return '<u>Hello World!</u>'


@app.route('/imdb/artists/<prefix>')
def get_artists_by_prefix(prefix):
    res = IMDBArtistResource.get_by_name_prefix(prefix)
    rsp = Response(json.dumps(res), status=200, content_type="application/json")
    return rsp


#
# @app.route('/<db_schema>/<table_name>/<column_name>/<prefix>')
# def get_by_prefix(db_schema, table_name, column_name, prefix):
#     res = RDBService.get_by_prefix(db_schema, table_name, column_name, prefix)
#     rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
#     return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
