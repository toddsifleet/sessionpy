
class Column(object):
  def __init__(self, name, unique = False, **kwargs):
    self.name = name
    self.unique = unique
    self.args = kwargs

  def is_unique(self):
    return self.unique

  def create_args(self):
    args = {
      'unique': self.unique
    }
    args.update(self.args)
    return (self.name, self.column_type, self.args)

class String(Column):
  column_type = 'string'

class DateTime(Column):
  column_type = 'datetime'

class Integer(Column):
  column_type = 'integer'

class PrimaryKey(Column):
  column_type = 'primary_key'

  def is_unique(self):
    return True
