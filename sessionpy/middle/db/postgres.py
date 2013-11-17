import psycopg2
from base import Connection

class Connection(Connection):
  primary_key_sql = 'id serial primary key'
  text_sql = 'VARCHAR(240)'
  bind_char = '%s'
  def connect(self, db_name):
    self.connection = psycopg2.connect("dbname=test user=toddsifleet")
    self.cursor = self.connection.cursor()
