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
    path_to_config = path_to_config
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

  def init_tables(self):
    self._call_on_models('init_table')

  def drop_tables(self):
    self._call_on_models('drop_table')

  def _call_on_models(self, method_name):
    from models.user import User
    from models.session import Session
    getattr(User, method_name)()
    getattr(Session, method_name)()
    if hasattr(self.config, 'admin'):
      from models.admin import AdminUser, AdminSession
      getattr(AdminUser, method_name)()
      getattr(AdminSession, method_name)()



