import MySQLdb as mdb
import MySQLdb.cursors
from base import Connection

class Connection(Connection):
  create_sql = 'CREATE TABLE {table_name} ({columns}, PRIMARY KEY (id))'
  primary_key_sql = 'id MEDIUMINT NOT NULL AUTO_INCREMENT'
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

  def string_sql(self, *args, **kwargs):
    return 'VARCHAR(240)'

  def datetime_sql(self, *args, **kwargs):
    return 'TIMESTAMP'
