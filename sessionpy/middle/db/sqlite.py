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
    self.connection.execute('PRAGMA foreign_keys = ON;')
    self.connection.row_factory = dict_factory
    self.cursor = self.connection.cursor()
    self.table_manager = TableManager(self.connection, self.cursor)


class TableManager(base.TableManager):
  primary_key_sql = 'id integer primary key autoincrement'
  drop_table_sql = 'DROP TABLE IF EXISTS {table_name}'
  def string_sql(self, *args, **kwargs):
    return ''


  def primary_key_sql(self, *args, **kwargs):
    return 'integer primary key autoincrement'

  def table_constraints_sql(self, *columns):
    output = []
    foreign_keys = [c for c in columns if len(c) > 2 and 'foreign_key' in c[2]]
    for c in foreign_keys:
      table_name, foreign_name = c[2]['foreign_key']
      output.append('FOREIGN KEY({column}) REFERENCES {table_name}({foreign_name})'.format(
      column = c[0],
      table_name = table_name,
      foreign_name = foreign_name
    ))
    return output
