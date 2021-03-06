import psycopg2
import psycopg2.extras
import base

class Base(base.Base):
  def quote_if_needed(self, v):
    return v
    if v in ['user']:
      return '"' + v + '"'
    else:
      return v

class Connection(Base, base.Connection):
  def connect(self, *args, **kwargs):
    key_values = [a + '=' + b for a,b in kwargs.items()]
    self.connection = psycopg2.connect(" ".join(key_values))
    self.cursor = self.get_cursor()
    self.table_manager = TableManager(self.connection, self.cursor)

  def get_insert_sql(self, return_id):
    if return_id:
      return self.insert_sql + ' RETURNING id'
    return self.insert_sql

  def last_row_id(self, cursor = None):
    if cursor is None:
      cursor = self.cursor
    return cursor.fetchone()[0]

  def get_cursor(self):
    return self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


class TableManager(Connection, base.TableManager):
  def primary_key_sql(self, *args, **kwargs):
    return 'serial primary key'

