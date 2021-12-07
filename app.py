from flask import Flask, Response, request, redirect, url_for, sessions
from flask_cors import CORS
import json
import logging
from datetime import datetime

import utils.rest_utils as rest_utils

# from application_services.imdb_artists_resource import IMDBArtistResource
from application_services.MessageResource.message_service import MessageService
from database_services.RDBService import RDBService as RDBService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)


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

#get_all_inbox/POST: 在userA和userB之间创建message inbox TODO: dynamo
#get_all_inbox/GET: 获取userA和其他用户之间的所有message inbox if existed TODO: dynamo
#get_all_inbox/DELETE: 删除userA和userB之间的message inbox if existed TODO: dynamo DONE
@app.route("/api/inbox/", methods=["GET", "POST", "DELETE"])
def get_all_inbox():
    res = None
    scode = None
    if request.method == 'POST':
        # TODO: testing data validation. If a field is not null in db and invalid data, there is a default
        userA = 1
        userB = request.form['other_user']
        res = MessageService.post_inbox(userA, userB)
        print("[post_new_inbox] res", res)
        scode = None
        if res == 1:
            # Created Success!
            scode = 201
            rsp = Response('Inbox Created Success!', status=scode)
            print("rsp:", rsp)
            return rsp
    elif request.method == "DELETE":

        userA = 1
        userB = request.form['other_user']
        # res = MessageService.delete_inbox(userA, userB)
        inbox = MessageService.get_inbox_msg_for_users(int(userA), int(userB))
        print('inbox result: ', inbox)
        if inbox == -99:
            # Deletion Failed
            scode = 404
            rsp = Response('Inbox Not Existed!', status=scode)
            return rsp
        else:
            print('Found their inbox!')
            res1 = MessageService.delete_inbox_dynomo("inbox", 'inboxId', inbox) #删掉了inbox
            print("res: ", res1)

            res2 = MessageService.delete_usermsg_dynomo("user_message", 'inbox_id', inbox)  # 删掉了user_message
            print("res: ", res2)
            message_delete_res = res2['ResponseMetadata']['HTTPStatusCode']
            print('http res: ', message_delete_res)
            scode = message_delete_res
            rsp = Response('Delete Success!', status=scode)
            return rsp
        # if res == 1:
        #     # Deleted Success!
        #     scode = 204
        #     rsp = Response('Delete Success!', status=scode)
        #     return rsp
        # elif res == 0:
        #     # Deletion Failed
        #     scode = 404
        #     rsp = Response('Inbox Not Existed!', status=scode)
        #     return rsp
    elif request.method == 'GET':
        inbox_list = MessageService.get_all_inbox()
        inbox_users = []
        for inbox in inbox_list:
            print("inbox: ", inbox)
            inbox.pop('createdOn')
            inbox_users.append(inbox)
        print("users: ", inbox_users)
        if len(inbox_users) > 0:
            res = json.dumps(inbox_users)
            print("res: ", res)
            scode = 200
            rsp = Response(json.dumps(inbox_users), status=scode)
        else:
            scode = 404
            rsp = Response('Inbox Not Found!', status=scode)
        return rsp
    else:
        scode = 405
        rsp = Response('Invalid Method Calls!', status=scode)  # invalid method calls
        return rsp

    # logger.log("/api/messages/ received/returned")
    if res:
        return Response(json.dumps(res, default=str), status=scode, content_type="application/json")
    else:
        return Response(status=scode)

#get_msg_by_id/GET: 根据msgId获取对应msg TODO: dynamo
#get_msg_by_id/DELETE: 根据msgId删除对应msg TODO: dynamo
# Return individual messages is current user has access to inbox or if admin
# @app.route("/api/msg/<msg_id>", methods=["GET", "DELETE"])
@app.route("/api/msg/", methods=["GET", "DELETE"])
def get_msg_by_id(msg_id=None):
    res = None
    scode = None
    msg_id = request.args.get('msgId')
    if request.method == 'GET':
        res = MessageService.get_msg_by_id(msg_id)
        if len(res) > 0:
            scode = 200
        else:
            scode = 404
            rsp = Response('Message Not Found!', status=scode)
            return rsp
    elif request.method == 'DELETE':
        # msg_id = request.form['msgId']
        res = MessageService.delete_msg_by_id(msg_id)
        print('res: ',res)
        if res > 0:
            # Deleted Success!
            scode = 204
            rsp = Response('Delete Success!', status=scode)
            return rsp
        elif res <= 0:
            # Deletion Failed
            scode = 404
            rsp = Response('Message Not Existed!', status=scode)
            return rsp
        scode = 204
        rsp = Response(status=scode)
        return rsp
    else:
        scode = 405
        rsp = Response('Invalid Method Calls!', status=scode)  # invalid method calls
        return rsp

    # logger.log("/api/messages/ received/returned:\n", res.to_json())
    rsp = Response(json.dumps(res, default=str), status=scode, content_type="application/json")
    return rsp


# get_inbox_msg_for_users/GET: 获取userA和userB的message inbox中的所有msg TODO: dynamo(half DONE)
# get_inbox_msg_for_users/POST: create message for userA&userB TODO: dynamo
# Return all msgs in the inbox for a pair of users (NOT valid for admin role)
@app.route("/api/inbox/user/<user_id>/msg", methods=["GET", "POST"])
def get_inbox_msg_for_users(user_id=None):
    res = None
    scode = None
    userA = 1


    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            return redirect(url_for('get_all_inbox'))
        inbox = MessageService.get_inbox_msg_for_users(int(userA), int(user_id))
        print('inbox result: ', inbox)
        # if len(inbox) <= 0:
        if inbox <= 0:
            scode = 404
            rsp = Response('Message Not Found!', status=scode)
            return rsp
        else:
            scode = 204
            # rsp = Response('Delete Success!', status=scode)
            # return rsp
            return redirect(url_for('get_msg_by_index', inbox_id=inbox))
    elif request.method == 'POST':
        # POST new message:
        # user A select user B -> post message to user B -> if new conversation, create inbox; if not, add message to this inbox
        # select user (userA_id, userB_id) -> choose to post message (user_input)
        # -> check whether the inbox existed (inbox_id
        # -> 1) create inbox -> add message to this inbox; 2) get inbox -> add message to this inbox;
        user_id = request.form['user_id']
        message = request.form['message']
        inbox_existed = False
        print(userA, user_id)
        inbox = MessageService.get_inbox_msg_for_users(int(userA), int(user_id))
        print('inbox result: ', inbox)
        print('inbooooooox')
        if inbox > 0:
            print('inbox existed!')
            inbox_existed = True
            inbox_id = inbox
            res = MessageService.post_msg_by_inbox(inbox_id, userA, message)
            if res == 1:
                scode = 200
                rsp = Response('Sent Success!', status=scode)
                return rsp
        else:
            print('inbox not existed!')
            inbox_existed = False
            post_inbox_res = MessageService.post_inbox(userA, user_id)
            inbox_new = MessageService.get_inbox_msg_for_users(int(userA), int(user_id))
            if inbox_new > 0:
                inbox_existed = True
                inbox_id = inbox_new
                print('created inbox id: ', inbox_id)
                res = MessageService.post_msg_by_inbox(inbox_id, userA, message)
            else:
                scode = 404
                rsp = Response('Post Failed!', status=scode)
                return rsp
        print('new message rst: ', res)
        if res == 1:
            scode = 200
            rsp = Response('Sent Success! New Inbox Created!', status=scode)
            return rsp

    # elif request.method == 'DELETE':
        pass
    else:
        scode = 405
        rsp = Response('Invalid Method Calls!', status=scode)  # invalid method calls
        return rsp

    # logger.log("/api/messages/users/<user> received/returned:\n", res.to_json())
    return Response(json.dumps(res, default=str), status=200, content_type="application/json")


# TODO: create tmp data for all the inbox and msg that a given user is able to access?
# avoid checking authentication on every message page

#TODO: 这里如何通过index获得inboxId？
# get_msg_by_index(inbox_id)"GET": 通过inboxid获取这个inbox里面的所有message TODO:dynamo
# Return all msgs in a conversation if admin or if current user involved in the inbox
@app.route("/api/inbox/<inbox_id>/msg", methods=["GET", "DELETE"])
def get_msg_by_index(inbox_id):
    res = None
    scode = None
    if inbox_id is None:
        inbox_id = request.args.get('inboxId')
    if request.method == 'GET':
        res = MessageService.get_msg_by_inbox(inbox_id)
        print('res here:    ', res)
        if not res:
            scode = 404
            rsp = Response('Message Not Found!', status=scode)
            return rsp
        pass
    # elif request.method == 'POST':
        # pass
    elif request.method == 'DELETE':
        res = MessageService.delete_msg_by_inbox(inbox_id)
        if res<=0:
            scode = 404
            rsp = Response('Message Not Found!', status=scode)
            return rsp
        else:
            scode = 204
            rsp = Response('Delete Success!', status=scode)
            return rsp
    else:
        scode = 405
        rsp = Response('Invalid Method Calls!', status=scode)  # invalid method calls
        return rsp

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
    app.run(host="0.0.0.0", port=5050)
