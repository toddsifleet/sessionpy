from functools import partial

class Column(object):
  unique = False
  null = True
  def __init__(self, name, **kwargs):
    self.name = name
    self.unique = kwargs.pop('unique', self.unique)
    self.null = kwargs.pop('null', self.null)
    self.args = kwargs

  def is_unique(self):
    return self.unique

  def create_args(self):
    args = {
      'unique': self.unique,
      'not_null': not self.null
    }
    args.update(self.args)
    return (self.name, self.column_type, args)

  def update_model(self, model):
    return self.add_find_by(model)

  def add_find_by(self, model):
    name = 'find_by_' + self.name
    def find(unique, column, value):
      return model.select(column, value, unique)
    if self.is_unique():
      setattr(model, name, partial(find, True, self.name))
    else:
      setattr(model, name, partial(find, False, self.name))

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
  def __init__(self, model, null = True):
    self.null = null
    self.related_type = model
    self.name = model.name
    self.args = {
      'foreign_key': (model.table_name, 'id')
    }

  def update_model(self, model):
    def find(p):
      return self.related_type.find_by_id(p.id)

    setattr(model, 'fetch_' + self.name, find)

    def find(p):
      return model.select(self.name, p.id, False)

    setattr(self.related_type, model.name + 's', find)

    self.add_find_by(model)
    self.related_type.add_dependent(model)

class Dependent(Relationship):
  unique = True

class Owner(Relationship):
  pass
