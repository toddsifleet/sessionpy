import MySQLdb as mdb
import MySQLdb.cursors
import base


class Connection(base.Connection):
  bind_char = '%s'
  def connect(self, db_name):
    self.connection = mdb.connect(
      'localhost',
      'testuser',
      'test623',
      'sessionpy_test',
      cursorclass = MySQLdb.cursors.DictCursor
    )

    self.cursor = self.connection.cursor()
    self.table_manager = TableManager(self.connection, self.cursor)

  def datetime_sql(self, *args, **kwargs):
    return 'TIMESTAMP'


class TableManager(base.TableManager):
  create_sql = 'CREATE TABLE {table_name} ({columns}, PRIMARY KEY (id) {after_sql})'
  primary_key_sql = 'id MEDIUMINT NOT NULL AUTO_INCREMENT'

  def integer_sql(self, *args, **kwargs):
    return 'MEDIUMINT'
