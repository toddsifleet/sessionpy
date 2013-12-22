import MySQLdb as mdb
import MySQLdb.cursors
import base


class Connection(base.Connection):
  bind_char = '%s'
  def connect(self, *args, **kwargs):
    self.connection = mdb.connect(
      kwargs['host'],
      kwargs['user'],
      kwargs['password'],
      kwargs['db'],
      cursorclass = MySQLdb.cursors.DictCursor
    )

    self.cursor = self.get_cursor()
    self.table_manager = TableManager(self.connection, self.cursor)


class TableManager(base.TableManager):
  create_sql = 'CREATE TABLE {table_name} ({columns})'

  def integer_sql(self, *args, **kwargs):
    return 'MEDIUMINT'

  def primary_key_sql(self, *args, **kwargs):
    return 'MEDIUMINT NOT NULL AUTO_INCREMENT'

  def primary_key_table_sql(self, column_name):
    return 'PRIMARY KEY ({column_name})'.format(column_name = column_name)

  def datetime_sql(self, *args, **kwargs):
    return 'TIMESTAMP DEFAULT 0'

