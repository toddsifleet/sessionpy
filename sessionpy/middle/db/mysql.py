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

    self.cursor = self.get_cursor()
    self.table_manager = TableManager(self.connection, self.cursor)

  def datetime_sql(self, *args, **kwargs):
    return 'TIMESTAMP'


class TableManager(base.TableManager):
  create_sql = 'CREATE TABLE {table_name} ({columns})'

  def integer_sql(self, *args, **kwargs):
    return 'MEDIUMINT'

  def primary_key_sql(self, *args, **kwargs):
    return 'MEDIUMINT NOT NULL AUTO_INCREMENT'

  def primary_key_table_sql(self, column_name):
    return 'PRIMARY KEY ({column_name})'.format(column_name = column_name)
