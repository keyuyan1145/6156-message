from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService


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
    def get_inbox_msg_for_users(cls, cur_user, other_user):
        user1 = min(cur_user, other_user)
        user2 = max(cur_user, other_user)
        fields = {'user1': user1, 'user2': user2}
        res1 = RDBService.find_by_template('chat', 'inbox', fields)
        # print("res : ", res1)
        # res = RDBService.find_by_template('chat', 'msg', {'inbox': res1['inboxId']})
        # print('[get_inbox_msg_for_user] res:', res)
        return res1[0]['inboxId']

    @classmethod
    def get_all_inbox(cls):
        # res = RDBService.find_by_template('chat', 'messages')
        # print('[MessageService.get_all_messages] res: ', res)
        # return res
        return RDBService.find_by_template('chat', 'inbox')

    @classmethod
    def get_msg_by_id(cls, msg_id):
        if msg_id:
            return RDBService.find_by_template('chat', 'msg', {'msgId': msg_id})
        else:
            return RDBService.find_by_template('chat', 'msg')

    @classmethod
    def get_msg_by_inbox(cls, inbox_id):
        return RDBService.find_by_template('chat', 'msg', {'inbox': inbox_id})

