
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
