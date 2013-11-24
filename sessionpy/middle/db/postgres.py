import psycopg2
import psycopg2.extras
from base import Connection

class Connection(Connection):
  primary_key_sql = 'id serial primary key'
  insert_sql = Connection.insert_sql + ' RETURNING id'
  text_sql = 'VARCHAR(240)'
  def connect(self, db_name):
    self.connection = psycopg2.connect("dbname=test user=toddsifleet")
    self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

  def last_row_id(self):
    return self.cursor.fetchone()[0]

