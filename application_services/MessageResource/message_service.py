from application_services.BaseApplicationResource import BaseRDBApplicationResource
# from dynamo.dynamodb import
from utils.select_fields_by_route import SELECT_FIELDS_BY_ROUTE
# from dynamo import dynamodb as RDBService
from database_services.RDBService import RDBService
from dynamo.dynamodb import delete_by_key,write_comment_if_not_changed,get_item
import copy
class MessageService(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def get_data_resource_info(cls):
        pass

    @classmethod
    def get_inbox_msg_for_users_dynamo(cls, cur_user, other_user):
        user1 = min(cur_user, other_user)
        user2 = max(cur_user, other_user)
        fields = {'user1': user1, 'user2': user2}
        res1 = RDBService.find_by_template('chat', 'inbox', fields)
        # res1 = RDBService.find_by_template('inbox', fields)
        print('res: ', res1)
        if not res1['Items']:
            print('inbox not existed between these users.')
            return -99
        else:
            print(type(res1))
            return res1['Items'][0]['inboxId']

    @classmethod
    def get_inbox_msg_for_users(cls, cur_user, other_user):
        user1 = min(cur_user, other_user)
        user2 = max(cur_user, other_user)
        fields = {'user1': user1, 'user2': user2}
        res1 = RDBService.find_by_template('chat', 'inbox', fields)
        # res1 = RDBService.find_by_template('inbox', fields)
        print('res: ', res1)
        # if not res1['Items']:
        if not res1:
            print('inbox not existed between these users.')
            return -99
        else:
            print(type(res1))
            return res1[0]['inboxId']

    @classmethod
    def get_all_inbox(cls, user1_id, user2_id):
        # res = RDBService.find_by_template('chat', 'messages')
        # print('[MessageService.get_all_messages] res: ', res)
        # return res
        fields = SELECT_FIELDS_BY_ROUTE['inbox']
        res = RDBService.find_by_template('chat', 'inbox', {'user1': int(user1_id), 'user2': int(user2_id)}, res_field=fields)
        # res = RDBService.find_by_template('inbox', fields)
        print('res:',res)
        return res

    @classmethod
    def get_oneuser_all_inbox(cls, user1_id):
        fields = SELECT_FIELDS_BY_ROUTE['inbox']
        res = RDBService.find_by_or_template('chat', 'inbox', {'user1': int(user1_id), 'user2': int(user1_id)}, res_field=fields)
        print('res:',res)
        return res


    @classmethod
    def post_inbox(cls, userA=None, userB=None):
        # user1 = min(userA, userB)
        # user2 = max(userA, userB)
        return RDBService.create('chat', 'inbox', {'user1': str(userA), 'user2': str(userB)})

    @classmethod
    def delete_inbox(cls, userA=None, userB=None):
        # user1 = min(userA, userB)
        # user2 = max(userA, userB)
        # return RDBService.delete('chat', 'inbox', {'user1': str(userA), 'user2': str(userB)})
        return RDBService.delete('chat', 'inbox', {'user1': str(userA), 'user2': str(userB)})

    @classmethod
    def delete_inbox_dynomo(cls, table_name, key_name, key_value):
        # user1 = min(userA, userB)
        # user2 = max(userA, userB)
        # return RDBService.delete('chat', 'inbox', {'user1': str(userA), 'user2': str(userB)})
        return delete_by_key(table_name, key_name, key_value)

    @classmethod
    def delete_usermsg_dynomo(cls, table_name, key_name, key_value):
        # user1 = min(userA, userB)
        # user2 = max(userA, userB)
        # return RDBService.delete('chat', 'inbox', {'user1': str(userA), 'user2': str(userB)})
        return delete_by_key(table_name, key_name, key_value)

    @classmethod
    def get_msg_by_id(cls, msg_id):
        fields = SELECT_FIELDS_BY_ROUTE['msg']
        if msg_id:
            return RDBService.find_by_template('chat', 'msg', {'msgId': msg_id}, res_field=fields)
        else:
            return RDBService.find_by_template('chat', 'msg', res_field=fields)

    @classmethod
    def delete_msg_by_id_dynamo(cls, msg_id):
        return delete_by_key('chat', 'msg', {'msgId': msg_id})

    @classmethod
    def delete_msg_by_id(cls, msg_id):
        return RDBService.delete('chat', 'msg', {'msgId': msg_id})

    @classmethod
    def get_msg_by_inbox(cls, inbox_id):
        fields = SELECT_FIELDS_BY_ROUTE['msg']
        # return dynamodb.get_item('user_message',1)
        print('inbox_id in sql: ', inbox_id)
        return RDBService.find_by_template('chat', 'msg', {'inbox': inbox_id}, res_field=fields, sort={'timestamp': 'asc'})

    @classmethod
    def delete_msg_by_inbox(cls, inbox_id):
        # fields = SELECT_FIELDS_BY_ROUTE['msg']
        # return RDBService.find_by_template('chat', 'msg', {'inbox': inbox_id}, res_field=fields, sort={'timestamp': 'asc'})
        return RDBService.delete('chat', 'msg', {'inbox': inbox_id})

    @classmethod
    def post_msg_by_inbox(cls, inbox_id, sender, message):
        return RDBService.create('chat', 'msg', {'inbox': int(inbox_id), 'sender': int(sender), 'msg': message})

    @classmethod
    def write_write(cls, userA, user_id):
        inbox_id = 1
        original_inbox = get_item("user_message", {"inbox_id": inbox_id})
        print('original inbox: ', original_inbox)
        original_version_id = original_inbox["version_id"]
        new_inbox = copy.deepcopy(original_inbox)

        try:
            res = write_comment_if_not_changed(original_inbox, new_inbox)
            print("First write returned: ", res)
        except Exception as e:
            print("First write exception = ", str(e))
        try:
            res = write_comment_if_not_changed(original_inbox, new_inbox)
            print("Second write returned: ", res)
        except Exception as e:
            raise e




