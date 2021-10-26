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
    def get_inbox_for_user(cls, user):
        # sql = f'select * from chat.msgInbox where user1={user} or user2={user}'
        # conn = RDBService._get_db_connection()
        # # print('got conn')
        # cur = conn.cursor()
        # res = cur.execute(sql)
        # # print("performed execution")
        # res = cur.fetchall()
        # # print('[MessageService.get_inbox_for_user] res: ', res)
        # wc, args = RDBService.find_by_template()
        # sql = "select * from aaaaF21.users left join aaaaF21.addresses on " + \
        #         "aaaaF21.primary_address_id = aaaaF21.addresses.id"
        #
        # res = RDBService.run_sql(sql, args, fetch=True)
        # return res
        pass


    @classmethod
    def get_all_inbox(cls):
        # res = RDBService.find_by_template('chat', 'messages')
        # print('[MessageService.get_all_messages] res: ', res)
        # return res
        return RDBService.find_by_template('chat', 'inbox')

    @classmethod
    def get_inbox_by_id(cls, inbox_id):
        return RDBService.find_by_template('chat', 'inbox', {'inboxId': inbox_id})

    @classmethod
    def get_msg_by_inbox(cls, inbox_id):
        # return RDBService.find_by_template('chat', 'messages', {'inboxId': inbox_id})
        # TODO: construct inner join
        pass

    @classmethod
    def get_inbox_by_user(cls, user_id):
        return RDBService.find_by_template('chat', 'messages', {'inboxId': user_id})
