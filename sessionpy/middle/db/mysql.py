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
  create_sql = 'CREATE TABLE {table_name} ({columns})'

  def integer_sql(self, *args, **kwargs):
    return 'MEDIUMINT'

  def primary_key_sql(self, *args, **kwargs):
    return 'MEDIUMINT'

  def table_constraints_sql(self, *columns):
    output = []
    for c in columns:
      if c[1] == 'primary_key':
        output.append('PRIMARY KEY ({id})'.format(id = c[0]))
    return output
