import psycopg2
import psycopg2.extras
import base


class Connection(base.Connection):
  insert_sql = base.Connection.insert_sql + ' RETURNING id'

  def connect(self, db_name):
    self.connection = psycopg2.connect("dbname=test user=toddsifleet")
    self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    self.table_manager = TableManager(self.connection, self.cursor)

  def last_row_id(self):
    return self.cursor.fetchone()[0]


class TableManager(base.TableManager):
  primary_key_sql = 'id serial primary key'
