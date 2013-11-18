import sqlite3
from base import Connection

class Connection(Connection):
  primary_key_sql = 'id integer primary key autoincrement'
  text_sql = ''
  bind_char = '?'
  def connect(self, db_name):
    self.connection = sqlite3.connect(db_name)
    self.cursor = self.connection.cursor()

