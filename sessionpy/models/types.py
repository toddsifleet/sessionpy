from functools import partial

class Column(object):
  unique = False
  def __init__(self, name, unique = False, **kwargs):
    self.name = name
    self.unique = unique or self.unique
    self.args = kwargs

  def is_unique(self):
    return self.unique

  def create_args(self):
    args = {
      'unique': self.unique
    }
    args.update(self.args)
    return (self.name, self.column_type, args)

  def to_db(self, value):
    return value

  def from_db(self, value):
    return value

  def update_model(self, model):
    name = 'find_by_' + self.name
    def find(unique, column, value):
      return model.select(column, value, unique)
    if self.is_unique():
      setattr(model, name, partial(find, True, self.name))
    else:
      setattr(model, name, partial(find, False, self.name))

  def to_db(self, value):
    return value

class String(Column):
  column_type = 'string'

class DateTime(Column):
  column_type = 'datetime'

class Integer(Column):
  column_type = 'integer'

class PrimaryKey(Column):
  column_type = 'primary_key'
  unique = True


class Relationship(Column):
  column_type = 'integer'
  def __init__(self, model):
    self.related_type = model
    self.name = model.name
    self.args = {
      'foreign_key': (model.table_name, 'id')
    }

  def to_db(self, model):
    if model:
      return model.id

  def update_model(self, model):
    def find(p):
      return self.related_type.find_by_id(p.id)

    setattr(model, 'fetch_' + self.name, find)
    model.add_dependent(self.related_type)

class Dependent(Relationship):
  unique = True

class Owner(Relationship):
  pass
