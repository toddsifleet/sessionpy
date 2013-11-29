from functools import partial
from datetime import datetime

class Column(object):
  def __init__(self, name, unique = False, **kwargs):
    self.name = name
    self.unique = unique

  def is_unique(self):
    return self.unique

  def create_args(self):
    return (self.name, self.column_type, {
      'unique':  self.unique,
    })

class String(Column):
  column_type = 'string'

class DateTime(Column):
  column_type = 'datetime'

class Integer(Column):
  column_type = 'integer'

class PrimaryKey(Column):
  column_type = 'primary_key'
  unique = True

  def is_unique(self):
    return True

class ModelMeta(type):
  def __init__(self, *args):
    type.__init__(self, *args)
    if hasattr(self, 'columns'):
      self.update_columns()
      self.set_column_names()
      self.add_filters()
    self.set_table_name(args[0])

  def update_columns(self):
    self.columns = (PrimaryKey('id', primary_key = True), ) + self.columns + self.audit_columns

  def add_filters(self):
    def find(unique, column, value):
      return self.select(column, value, unique)

    for c in self.columns:
      name = 'find_by_' + c.name
      if c.is_unique():
        setattr(self, name, partial(find, True, c.name))
      else:
        setattr(self, name, partial(find, False, c.name))

  def set_table_name(self, name):
    if not name == 'Model':
      self.table_name = name.lower() + 's'

  def set_column_names(self):
    self.column_names = [c.name for c in self.columns]
    self.audit_names = [c.name for c in self.audit_columns]

class Model(object):
  __metaclass__ = ModelMeta
  audit_columns = (
    DateTime('created_at'),
    DateTime('updated_at'),
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
    names = [c.name for c in self.columns]
    values = dict(zip(names, self.values())[1::])
    self.id = self.db.insert(
      self.table_name,
      True,
      **values
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
    columns = [c.create_args() for c in cls.columns]
    cls.db.table_manager.create_table(cls.table_name, *columns)

  @classmethod
  def drop_table(cls):
    cls.db.table_manager.drop_table(cls.table_name)

