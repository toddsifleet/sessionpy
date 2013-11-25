from functools import partial
from datetime import datetime

class ModelMeta(type):
  def __init__(self, *args):
    type.__init__(self, *args)
    if hasattr(self, 'columns'):
      self.update_columns()
      self.set_column_names()
      self.add_filters()
    self.set_table_name(args[0])

  def update_columns(self):
    self.columns = (('id', 'primary_key'), ) + self.columns + self.audit_columns

  def add_filters(self):
    for c in self.column_names:
      setattr(self, 'find_by_' + c, partial(self.select, c))

  def set_table_name(self, name):
    if not name == 'Model':
      self.table_name = name.lower() + 's'

  def set_column_names(self):
    self.column_names = [c[0] for c in self.columns]
    self.audit_names = [c[0] for c in self.audit_columns]

class Model(object):
  __metaclass__ = ModelMeta
  audit_columns = (
    ('created_at', 'datetime'),
    ('updated_at', 'datetime')
  )

  def __init__(self, **kwargs):
    self.id = None
    for c in self.audit_names:
      if c not in kwargs:
        kwargs[c] = datetime.today().replace(microsecond=0)
    for c, v in kwargs.items():
      setattr(self, c, v)

  def insert(self):
    names = [c[0] for c in self.columns]
    values = dict(zip(names, self.values())[1::])
    self.id = self.db.insert(
      self.table_name,
      **values
    )
    return self

  def values(self):
    return [getattr(self, k[0]) for k in self.columns]

  def put(self):
    self.db.update(
      self.table_name,
      **self.to_dict()
    )
    return self

  def to_dict(self):
    return dict(zip(self.columns, self.values()))

  def update(self, **kwargs):
    self.updated_at = datetime.today()
    for k, v in kwargs.items():
      setattr(self, k, v)
    self.db.update(
      self.table_name,
      id = self.id,
      updated_at = self.updated_at,
      **kwargs
    )

    return self

  def delete(self):
    self.db.delete(
      self.table_name,
      self.id
    )

  @classmethod
  def create(cls, **kwargs):
    return cls(**kwargs).insert()

  @classmethod
  def _from_row(cls, row):
    if row:
      return cls(**row)

  @classmethod
  def sql(cls, input, binds = ()):
    return cls.db.sql(input, binds)

  @classmethod
  def select(cls, column, value):
    result = cls.db.select(cls.table_name, column, value)
    return cls._from_row(result)

  @classmethod
  def init_table(cls):
    cls.db.table_manager.create_table(cls.table_name, *cls.columns[1:])

  @classmethod
  def drop_table(cls):
    cls.db.table_manager.drop_table(cls.table_name)
