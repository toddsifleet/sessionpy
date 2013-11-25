import sqlite3
import base

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
  return d

class Connection(base.Connection):
  bind_char = '?'
  def connect(self, db_name):
    self.connection = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
    self.connection.row_factory = dict_factory
    self.cursor = self.connection.cursor()
    self.table_manager = TableManager(self.connection, self.cursor)


class TableManager(base.TableManager):
  primary_key_sql = 'id integer primary key autoincrement'
  def string_sql(self, *args, **kwargs):
    return ''

