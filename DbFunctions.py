from ConfigParser import RawConfigParser
import _mysql
import os


class _ImageWeatherDb:
    _configparser = None
    mysql_user = None
    db_conn = None
    _prev_resIter = None

    class _DbResultIter:
        cursor = None
        _res_cursor = None

        def __init__(self, cursor):
            self.cursor = cursor

        def insertid(self):
            return self.cursor.insert_id()

        def next(self, result_count=1):
            # print "Cursor:", self.cursor, "Res:", self._res_cursor
            if self._res_cursor is None:
                # print "Getting the result from database",
                self._res_cursor = self.cursor.use_result()
                # print self._res_cursor

            if self._res_cursor is not None:
                # print "Fetching Result_column",
                _res = self._res_cursor.fetch_row(result_count)
                # print _res
                return _res


        def all(self):
            if self._res_cursor is None:
                self._res_cursor = self.cursor.store_result()
            if self._res_cursor is not None:
                _res = self._res_cursor.fetch_row(0)
                return _res
            else:
                return None


    def __init__(self, config=''):
        self._configparser = RawConfigParser(allow_no_value=True)
        if config == '':
            cfg_file = open(os.getenv('CFG_PATH'), 'r')
        else:
            cfg_file = open(config, 'r')
        self._configparser.readfp(cfg_file)

        if os.getenv('DEVELOPMENT', "0") == '1':
            self.mysqlhost = self._configparser.get('mysql_development', 'db_host')
            self.mysqlname = self._configparser.get('mysql_development', 'db_name')
            self.mysqluser = self._configparser.get('mysql_development', 'db_user')
            self.mysqlpass = self._configparser.get('mysql_development', 'db_pass')
        else:
            self.mysqlhost = self._configparser.get('mysql_production', 'db_host')
            self.mysqlname = self._configparser.get('mysql_production', 'db_name')
            self.mysqluser = self._configparser.get('mysql_production', 'db_user')
            self.mysqlpass = self._configparser.get('mysql_production', 'db_pass')

        db_conn = self._get_conn()
        db_conn.close()

    def _get_conn(self):
        # logger.info("Connecting DB Host:%s User:%s DB:%s", self.mysqlhost, self.mysqluser, self.mysqlname)
        return _mysql.connect(self.mysqlhost, self.mysqluser, self.mysqlpass, self.mysqlname)

    def _closedb(self, conn):
        conn.close()

    def execute(self, sql_query, new_conn=False):
        _conn = None
        if new_conn is True:
            _conn = self._get_conn()
        else:
            if self.db_conn is None:
                self.db_conn = self._get_conn()
                _conn = self.db_conn
            else:
                _conn = self.db_conn

            if self._prev_resIter is not None:
                self._prev_resIter.all()

        _conn.query(sql_query)

        self._prev_resIter = self._DbResultIter(_conn)
        return self._prev_resIter