import psycopg2
import psycopg2.extras
import base


class Connection(base.Connection):
  def connect(self, db_name):
    self.connection = psycopg2.connect("dbname=test user=toddsifleet")
    self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    self.table_manager = TableManager(self.connection, self.cursor)

  def get_insert_sql(self, return_id):
    if return_id:
      return self.insert_sql + 'RETURNING id'
    return self.insert_sql

  def last_row_id(self):
    return self.cursor.fetchone()[0]

class TableManager(base.TableManager):
  def primary_key_sql(self, *args, **kwargs):
    return 'serial primary key'
