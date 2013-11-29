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
    def find(unique, column, value):
      return self.select(column, value, unique)

    for c in self.columns:
      name = 'find_by_' + c[0]
      if c[1] == 'primary_key' or len(c) > 2 and 'unique' in c[2]:
        setattr(self, name, partial(find, True, c[0]))
      else:
        setattr(self, name, partial(find, False, c[0]))

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
    for c in self.column_names:
      v = kwargs.get(c, None)
      setattr(self, c, v)

  def insert(self):
    names = [c[0] for c in self.columns]
    values = dict(zip(names, self.values())[1::])
    self.id = self.db.insert(
      self.table_name,
      True,
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
        raise Exception("{name} Model does not have the attribute `{c}`".format(
          name = cls.table_name,
          c = c
        ))
    return cls(**kwargs).insert()

  @classmethod
  def _from_row(cls, row):
    return cls(**row)

  @classmethod
  def sql(cls, input, binds = ()):
    return cls.db.sql(input, binds)

  @classmethod
  def select(cls, column, value, unique = True):
    result = cls.db.select(cls.table_name, column, value)
    if unique:
      return cls._from_row(result.first)
    else:
      return (cls._from_row(x) for x in result)

  @classmethod
  def init_table(cls):
    cls.db.table_manager.create_table(cls.table_name, *cls.columns)

  @classmethod
  def drop_table(cls):
    cls.db.table_manager.drop_table(cls.table_name)
