import os

from flask import Flask, Response, request, redirect, url_for, session, render_template
from flask_cors import CORS
import json
import logging
from datetime import datetime

import utils.rest_utils as rest_utils
from flask_dance.contrib.google import make_google_blueprint, google

# from application_services.imdb_artists_resource import IMDBArtistResource
from application_services.MessageResource.message_service import MessageService
from database_services.RDBService import RDBService as RDBService
from middleware import security

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__, template_folder='template')
# app = Flask(__name__)
CORS(app)

# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
# os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
#
# app.secret_key = "supersekrit"
# blueprint = make_google_blueprint(
#     client_id="314377796932-bcks1e2lbvpi2v6crbb65alcgkpl6l9i.apps.googleusercontent.com",
#     client_secret="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",
#     scope=["profile", "email"],
#     redirect_to="/"
# )
#
# app.register_blueprint(blueprint, url_prefix="/login")


# g_bp = app.blueprints.get("google")

@app.before_request
def before_request_func():
    print("running before_request_func")
    if not security.check_security(request, session) and not google.authorized:
        return render_template('auth-err.html')

@app.after_request
def after_request_func(response):
    print("running after_request_func")
    return response


##################################################################################################################

@app.route('/')
def hello_world():
    return '<u>Hello World!</u>'


# DFF TODO A real service would have more robust health check methods.
# This path simply echoes to check that the app is working.
# The path is /health and the only method is GETs
@app.route("/health", methods=["GET"])
def health_check():
    rsp_data = {"status": "healthy", "time": str(datetime.now())}
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp

############################################################################################

# Handles all login information and process
# @app.route("/login")
# def login():
#     print("[/login] Inside the login page")
#     if not google.authorized:
#         print("[/login] before redirect to google")
#         return redirect(url_for("google.login"))
#
#     resp = google.get('/oauth2/v2/userinfo')
#     assert(resp.ok, resp.text)
#     print("------ User info returned from Google -------------")
#     print(resp.json, indent=2)
#     print("---------------------------------------------------")
#     return "You are {email} on Google".format(email=resp.json()["emails"][0]["value"])


# Return all inboxes if admin role else return inboxes related to user
@app.route("/api/inbox/", methods=["GET", "POST", "DELETE"])
def get_all_inbox():
    res = None
    scode = None
    if request.method == 'POST':
        # TODO: testing data validation. If a field is not null in db and invalid data, there is a default
        userA = 1
        # userB = request.form['other_user']
        userB = 10
        res = MessageService.post_inbox(userA, userB)
        print("[post_new_inbox] res", res)
        scode = 201
        pass
    elif request.method == "DELETE":
        scode = 204
        pass
    elif request.method == 'GET':
        res = MessageService.get_all_inbox()
        scode = 200
    else:
        scode = 405

    # logger.log("/api/messages/ received/returned")
    if res:
        return Response(json.dumps(res, default=str), status=scode, content_type="application/json")
    else:
        return Response(status=scode)


# Return individual messages is current user has access to inbox or if admin
@app.route("/api/msg/<msg_id>", methods=["GET", "DELETE"])
@app.route("/api/msg/", methods=["GET"])
def get_msg_by_id(msg_id=None):
    res = None
    scode = None
    if request.method == 'GET':
        res = MessageService.get_msg_by_id(msg_id)
        scode = 200
    elif request.method == 'DELETE':
        pass
    else:
        pass  # invalid method calls

    # logger.log("/api/messages/ received/returned:\n", res.to_json())
    rsp = Response(json.dumps(res, default=str), status=scode, content_type="application/json")
    return rsp


# TODO: need this?
# Return all msgs in the inbox for a pair of users (NOT valid for admin role)
@app.route("/api/inbox/user/<user_id>/msg", methods=["GET", "POST", "DELETE"])
def get_inbox_msg_for_users(user_id=None):
    res = None
    scode = None
    if not user_id:
        return redirect(url_for('get_all_inbox'))
    if request.method == 'GET':
        inbox = MessageService.get_inbox_msg_for_users(1, int(user_id))
        return redirect(url_for('get_msg_by_index', inbox_id=inbox))
    elif request.method == 'POST':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        pass  # invalid method calls

    # logger.log("/api/messages/users/<user> received/returned:\n", res.to_json())
    return Response(json.dumps(res, default=str), status=200, content_type="application/json")


# TODO: create tmp data for all the inbox and msg that a given user is able to access?
# avoid checking authentication on every message page

# Return all msgs in a conversation if admin or if current user involved in the inbox
@app.route("/api/inbox/<inbox_id>/msg", methods=["GET", "POST", "DELETE"])
def get_msg_by_index(inbox_id):
    res = None
    scode = None
    if request.method == 'GET':
        res = MessageService.get_msg_by_inbox(inbox_id)
        pass
    elif request.method == 'POST':
        pass
    elif request.method == 'DELETE':
        pass
    else:
        # invalid method
        pass

    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp


# -----------------------------------------------------------------------------------------
# EXAMPLEs:

# #Return all msgs in a conversation if admin or if current user involved in the inbox
# @app.route("/api/inbox/<inbox_id>/msg", methods=["GET", "POST", "DELETE"])
# def get_inbox_by_id(inbox_id):
#     # TODO -- We should wrap with an exception pattern.
#
#     # Mostly for isolation. The rest of the method is isolated from the specifics of Flask.
#     inputs = rest_utils.RESTContext(request, {"inbox_id": inbox_id})
#
#     msg = {
#         "/get_conversation received the following inputs": inputs.to_json()
#     }
#     # print(msg)
#     # logger.log("/api/message/<messagesId> received/returned:\n", msg)
#
#     res = MessageService.get_inbox_by_id(inbox_id)
#     rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
#     return rsp

# @app.route('/imdb/artists/<prefix>')
# def get_artists_by_prefix(prefix):
#     res = IMDBArtistResource.get_by_name_prefix(prefix)
#     rsp = Response(json.dumps(res), status=200, content_type="application/json")
#     return rsp


#
# @app.route('/<db_schema>/<table_name>/<column_name>/<prefix>')
# def get_by_prefix(db_schema, table_name, column_name, prefix):
#     res = RDBService.get_by_prefix(db_schema, table_name, column_name, prefix)
#     rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
#     return rsp

# --------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
