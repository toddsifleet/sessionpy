import imp
from models.base import Model
from middle.db import mysql, postgres, sqlite

backends = {
  'mysql': mysql,
  'postgres': postgres,
  'sqlite': sqlite
}

class Authenticator(object):
  def __init__(self, path_to_config, **kwargs):
    path_to_config = '/Users/toddsifleet/Dropbox/github/sessionpy/tests/models/' + path_to_config
    self.load_config(path_to_config, **kwargs)
    db_type = self.config.db.pop('type')
    self.connect(db_type, **self.config.db)
    Model.db = self.db

  def load_config(self, path_to_config, **kwargs):
    config = imp.load_source('sessionpy.config', path_to_config)
    for k, v in kwargs.items():
      if hasattr(config, k):
        getattr(config, k).update(v)
    self.config = config

  def connect(self, db_type, *args, **kwargs):
    self.db = backends[db_type].Connection(*args, **kwargs)




