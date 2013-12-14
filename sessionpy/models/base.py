from functools import partial
import re
from datetime import datetime

from types import DateTime, PrimaryKey, Dependent

def propogate(func):
  def wrapper(self, *args, **kwargs):
    def call(m):
      f = getattr(m, func.func_name, None)
      if f:
        f(*args, **kwargs)

    map(call, self.dependents)
    return func(self, *args, **kwargs)
  return wrapper

class ModelMeta(type):
  def __init__(self, *args):
    type.__init__(self, *args)
    self.foreign_keys = {}
    self.dependents = []
    if hasattr(self, 'columns'):
      self.set_table_name(args[0])
      self.update_columns()
      self.set_column_names()
      self.add_filters()

  def update_columns(self):
    self.columns = (PrimaryKey('id'), ) + self.columns + self.audit_columns

  def add_filters(self):
    for c in self.columns:
      c.update_model(self)

  def set_table_name(self, name):
    if not name == 'Model':
      self.name = camel_to_snake(name)
      self.table_name = self.name + 's'

  def set_column_names(self):
    self.column_names = [c.name for c in self.columns]
    self.audit_names = [c.name for c in self.audit_columns]

class Model(object):
  __metaclass__ = ModelMeta
  audit_columns = (
    DateTime('created_at'),
    DateTime('updated_at'),
  )
  table_name = None

  def __init__(self, **kwargs):
    self.id = None
    for c in self.audit_names:
      if c not in kwargs:
        kwargs[c] = datetime.today().replace(microsecond=0)

    for c in self.column_names:
      v = kwargs.get(c, None)
      setattr(self, c, v)

  @classmethod
  def to_db(self, v):
    if hasattr(v, 'id'):
      return v.id
    return v

  @classmethod
  def from_db(self, v):
    return v

  def insert(self):
    keys = [c.name for c in self.columns]
    values = map(self.to_db, self.values())
    kwargs = dict(zip(keys,values)[1::])
    self.id = self.db.insert(
      self.table_name,
      True,
      **kwargs
    )
    return self

  def values(self):
    return [getattr(self, k.name) for k in self.columns]

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

  def __eq__(self, other_model):
    if not isinstance(other_model, type(self)):
      return False

    for x, y in zip (self.values(), other_model.values()):
      if not x == y:
        return False
    return True

  @classmethod
  def create(cls, **kwargs):
    for c in kwargs:
      if c not in cls.column_names:
        raise Exception(cls.column_names)
        raise Exception("{name} Model does not have the attribute `{c}`".format(
          name = cls.table_name,
          c = c
        ))
    return cls(**kwargs).insert()

  @classmethod
  def _from_row(cls, row):
    args = {}
    for x in row:
      args[x] = cls.from_db(row[x])
    return cls(**args)

  @classmethod
  def sql(cls, input, binds = ()):
    return cls.db.sql(input, binds)

  @classmethod
  def select(cls, column, value, unique = True):
    v = value.id if hasattr(value, 'id') else value
    result = cls.db.select(cls.table_name, column, v)
    if unique:
      return cls._from_row(result.first)
    else:
      return (cls._from_row(x) for x in result)

  @classmethod
  def init_table(cls):
    cls.db.table_manager.create_table(cls.table_name, *[
      c.create_args() for c in cls.columns
    ])

  @classmethod
  @propogate
  def drop_table(cls):
    cls.db.table_manager.drop_table(cls.table_name)

  @classmethod
  def add_dependent(self, model):
    self.dependents.append(model)

_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')

def camel_to_snake(s):
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()
