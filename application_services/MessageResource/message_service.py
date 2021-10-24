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

    # @classmethod
    # def get_by_name_prefix(cls, name_prefix):
    #     res = RDBService.get_by_prefix("IMDBFixed", "name_basics",
    #                                   "primaryName", name_prefix)
    #     return res

    @classmethod
    def get_inbox_for_user(cls, user):
        sql = f'select * from chat.msgInbox where user1={user} or user2={user}'
        conn = RDBService._get_db_connection()
        print('got conn')
        cur = conn.cursor()
        res = cur.execute(sql)
        print("performed execution")
        res = cur.fetchall()
        # res = RDBService.run_sql(sql, None, True)
        print('[MessageService.get_inbox_for_user] res: ', res)
        return res

    @classmethod
    def get_msg_for_inbox(cls, inbox):
        pass