import MySQLdb as mdb
import MySQLdb.cursors
from base import Connection

class Connection(Connection):
  create_sql = 'CREATE TABLE {table_name} ({columns}, PRIMARY KEY (id))'
  primary_key_sql = 'id MEDIUMINT NOT NULL AUTO_INCREMENT'
  datetime_sql = 'DATETIME'
  string_sql = 'VARCHAR(240)'
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

