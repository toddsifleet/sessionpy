import sqlite3
from base import Connection

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
  return d

class Connection(Connection):
  primary_key_sql = 'id integer primary key autoincrement'
  text_sql = ''
  bind_char = '?'

  def connect(self, db_name):
    self.connection = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
    self.connection.row_factory = dict_factory
    self.cursor = self.connection.cursor()

