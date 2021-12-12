import json
import dynamodb as db
import copy
import uuid


# def t1():
#
#     res = db.get_item("comments",
#                       {
#                           "comment_id": "984b90ff-0887-4291-afc4-7854bf452ac8"
#                       })
#     print("Result = \n", json.dumps(res, indent=4, default=str))

#this is like find by pk
def t1():

    res = db.get_item("user_message",
                      {
                          "inbox_id": 1
                      })
    print("Result = \n", json.dumps(res, indent=4, default=str))

def t2():

    res = db.find_by_template("user_message",
                      {
                          "inbox_id": 1
                      })
    print("Result = \n", json.dumps(res, indent=4, default=str))


def t3():
    table_name = "user_message"
    inbox_id = 1
    sender = 10
    message = "Test for dynamodb"
    res = db.add_message(table_name, inbox_id, sender, message)


def t4():
    tag = 'Sports'
    res = db.find_by_tag(tag)
    print("Comments with tag 'science' = \n", json.dumps(res, indent=3, default=str))


def t5():
    print("Do a projection ...\n")
    res = db.do_a_scan("comments",
                       None, None, "#c, comment_id", {"#c": "comment"})
    print("Result = \n", json.dumps(res, indent=4, default=str))


# def t6():
#
#     comment_id = "984b90ff-0887-4291-afc4-7854bf452ac8"
#     original_comment = db.get_item("comments",{"comment_id": comment_id})
#     original_version_id = original_comment["version_id"]
#
#     new_comment = copy.deepcopy(original_comment)
#
#     try:
#         res = db.write_comment_if_not_changed(original_comment, new_comment)
#         print("First write returned: ", res)
#     except Exception as e:
#         print("First write exception = ", str(e))
#
#     try:
#         res = db.write_comment_if_not_changed(original_comment, new_comment)
#         print("Second write returned: ", res)
#     except Exception as e:
#         print("Second write exception = ", str(e))

def t6():

    inbox_id = 1
    original_inbox = db.get_item("user_message",{"inbox_id": inbox_id})
    original_version_id = original_inbox["version_id"]

    new_inbox = copy.deepcopy(original_inbox)

    try:
        res = db.write_comment_if_not_changed(original_inbox, new_inbox)
        print("First write returned: ", res)
    except Exception as e:
        print("First write exception = ", str(e))

    try:
        res = db.write_comment_if_not_changed(original_inbox, new_inbox)
        print("Second write returned: ", res)
    except Exception as e:
        print("Second write exception = ", str(e))



t1()
# t2()
# t3()
# t4()
#t5()
# t6()

