from middle.db.base import transform_rows, transform_row, Result
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

class classproperty(object):
  def __init__(self, getter):
    self._getter = getter

  def __get__(self, instance, owner):
    return self._getter(owner)

class ModelMeta(type):
  def __init__(self, model_name, *args):
    type.__init__(self, model_name, *args)
    if not model_name == 'Model':
      self.dependents = []
      self.set_table_name(model_name)
      self.update_columns()
      self.add_filters()

  def update_columns(self):
    columns = (PrimaryKey('id'), ) + self.columns + self.audit_columns
    column_name_map = dict([(c.name, c) for c in columns])
    columns = [column_name_map[c.name] for c in columns]

    self.columns = tuple(filter(bool, columns))

  def add_filters(self):
    for c in self.columns:
      c.update_model(self)

  def set_table_name(self, name):
    self.name = camel_to_snake(name)
    self.table_name = self.name + 's'

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

    for c in self.attr_names:
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
    kwargs = self.db_hash
    if kwargs.pop('id'):
        raise Exception('You can\'t insert a model with an id')
    for k,v in kwargs.items():
      if v is None:
        del kwargs[k]
    self.id = self.db.insert(
      self.table_name,
      True,
      **kwargs
    )
    return self

  @property
  def values(self):
    return [getattr(self, k.name) for k in self.columns]

  @classproperty
  def column_names(self):
    return [c.column_name for c in self.columns]

  @classproperty
  def audit_names(self):
    return [c.name for c in self.audit_columns]

  @classproperty
  def attr_names(self):
    return [c.name for c in self.columns]

  def put(self):
    self.db.update(
      self.table_name,
      **self.to_dict()
    )
    return self

  def to_dict(self):
    return dict(zip(self.attr_names, self.values))

  @property
  def db_hash(self):
    values = [self.to_db(v) for v in self.values]
    return dict(zip(self.column_names, values))

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
    self.dump()
    other_model.dump()
    for k, v in zip(self.attr_names, self.values):
      if not hasattr(other_model, k):
        return False

      other_v = self.to_db(getattr(other_model, k))
      if not other_v == self.to_db(v):
        return False
    return True

  def dump(self):
    for k, v in zip(self.attr_names, self.values):
      print k, v

  @classmethod
  def create(cls, **kwargs):
    for c in kwargs:
      if c not in cls.attr_names:
        raise Exception([cls.attr_names, cls.column_names])
        raise Exception("{name} Model does not have the attribute `{c}`".format(
          name = cls.table_name,
          c = c
        ))
    return cls(**kwargs).insert()

  @classmethod
  def _from_row(cls, row):
    if row is None:
      return None
    args = {}
    for c in cls.columns:
      args[c.name] = cls.from_db(row[c.column_name])
    return cls(**args)

  @classmethod
  def sql(cls, input, binds = ()):
    return cls.db.sql(input, binds)

  @classmethod
  def select(cls, column, value, unique = True, **kwargs):
    v = value.id if hasattr(value, 'id') else value
    result = cls.db.select(cls.table_name, column, v, **kwargs)
    if unique:
      return cls._from_row(result.first)
    else:
      return Result(cls, result)

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

class Result(Result):
  def __init__(self, model, source):
    self.model = model
    self.db = source.db
    self.select_params = source.select_params
    self.select_modifiers = source.select_modifiers

  def transform(self, row):
    return self.model._from_row(row)


_underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
_underscorer2 = re.compile('([a-z0-9])([A-Z])')

def camel_to_snake(s):
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()
