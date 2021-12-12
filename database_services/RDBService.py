import pymysql
import json
import logging

import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDBService:

    def __init__(self):
        pass

    @classmethod
    def _get_db_connection(cls):

        db_connect_info = context.get_db_info()

        logger.info("RDBService._get_db_connection:")
        logger.info("\t HOST = " + db_connect_info['host'])

        db_info = context.get_db_info()
        print(db_info)

        db_connection = pymysql.connect(
            **db_info,
            autocommit=True
        )
        print(db_connection)
        return db_connection

    @classmethod
    def run_sql(cls, sql_statement, args, fetch=False):

        conn = RDBService._get_db_connection()

        try:
            cur = conn.cursor()
            res = cur.execute(sql_statement, args=args)
            if fetch:
                res = cur.fetchall()
        except Exception as e:
            conn.close()
            raise e

        return res

    @classmethod
    def get_by_prefix(cls, db_schema, table_name, column_name, value_prefix):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name + " where " + \
              column_name + " like " + "'" + value_prefix + "%'"
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def get_where_clause_args(cls, template):

        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k, v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " where " + " AND ".join(terms)

        print('where clause: ', clause)
        return clause, args

    @classmethod
    def get_sort_clause(cls, fields):

        terms = []
        clause = None

        for k, v in fields.items():
            terms.append(k + " " + v)
        clause = " order by " + ",".join(terms)

        print(clause)
        return clause

    @classmethod
    def find_by_template(cls, db_schema, table_name, template=None, res_field=None, sort=None):

        wc, args = RDBService.get_where_clause_args(template)
        if res_field:
            print('res_field:', res_field)
            res_attr = ",".join(res_field)
        else:
            res_attr = "*"

        conn = RDBService._get_db_connection()
        cur = conn.cursor()


        print('res_attr:', res_attr)
        print('db_schema: ', db_schema)
        print('table_name: ', table_name)
        print('wc: ', wc)

        sql = "select " + res_attr + " from " + db_schema + "." + table_name + " " + wc
        print("[find_by_template] sql: ", sql)
        print('args: ', args)
        if sort:
            sql += RDBService.get_sort_clause(sort)

        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def create(cls, db_schema, table_name, create_data):

        cols = []
        vals = []
        args = []

        for k, v in create_data.items():
            cols.append(k)
            vals.append('%s')
            args.append(v)


        cols_clause = "(" + ",".join(cols) + ")"
        vals_clause = "values (" + ",".join(vals) + ")"

        sql_stmt = "insert into " + db_schema + "." + table_name + " " + cols_clause + \
                   " " + vals_clause

        print('[create] sql_stmt: ', sql_stmt)

        res = RDBService.run_sql(sql_stmt, args)
        return res

    @classmethod
    def delete(cls, db_schema, table_name, field_list):

        wc, args = RDBService.get_where_clause_args(field_list)

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "delete from " + db_schema + "." + table_name + " " + wc
        print("[delete] sql: ", sql)
        res = cur.execute(sql, args=args)

        conn.close()
        return res
