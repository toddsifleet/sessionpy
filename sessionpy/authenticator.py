from models.base import Model
from middle.db import mysql, postgres, sqlite

backends = {
  'mysql': mysql,
  'postgres': postgres,
  'sqlite': sqlite
}

class Authenticator(object):
  def __init__(self, db_type, *args, **kwargs):
    self.connect(db_type, *args, **kwargs)
    Model.db = self.db

  def connect(self, db_type, *args, **kwargs):
    self.db = backends[db_type].Connection(*args, **kwargs)




