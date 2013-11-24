
def transaction(func):
  def wrapper(self, *args, **kwargs):
    self.start_transaction()
    result = func(self, *args, **kwargs)
    self.commit()
    return result
  return wrapper

class Connection(object):
  select_sql = 'SELECT * FROM {table_name} WHERE {column} = {bind_char}'
  delete_sql = 'DELETE FROM {table_name} WHERE id = {bind_char}'
  insert_sql = 'INSERT INTO {table_name} ({columns}) VALUES ({values})'
  update_sql = 'UPDATE {table_name} SET {columns} WHERE id = {bind_char}'
  create_sql = 'CREATE TABLE {table_name} ({columns})'
  drop_table_sql = 'DROP TABLE IF EXISTS {table_name}'
  bind_char = '%s'

  def __init__(self, *args, **kwargs):
    self.connect(*args, **kwargs)

  def select(self, table_name, column, value):
    self.sql(self.select_sql, value,
      column = column,
      table_name = table_name
    )

    return self.get_row()

  def get_row(self):
    return self.cursor.fetchone()

  @transaction
  def delete(self, table_name, id):
    self.sql(self.delete_sql, id, table_name = table_name)

  @transaction
  def insert(self, table_name, **data):
    columns = data.keys()
    values = data.values()
    self.sql(self.insert_sql, *values,
      table_name = table_name,
      columns = ", ".join(columns),
      values = ", ".join([self.bind_char for x in columns])
    )
    return self.last_row_id()

  def last_row_id(self):
    return self.cursor.lastrowid

  @transaction
  def update(self, table_name, id, **data):
    columns = ", ".join([ c + ' = {bind_char}' for c in data])
    binds = data.values() + [id]
    self.sql(self.update_sql, *binds,
      table_name = table_name,
      columns = columns.format(bind_char = self.bind_char)
    )

  @transaction
  def create_table(self, table_name, *columns):
    columns  = (self.primary_key_sql,) +\
      tuple([self.column_sql(*c) for c in columns])
    self.sql(self.create_sql,
      table_name =  table_name,
      columns = ", ".join(columns),
    )

  @transaction
  def drop_table(self, table_name):
    self.sql(self.drop_table_sql, table_name = table_name)

  def commit(self):
    self.connection.commit()

  def start_transaction(self):
    self.cursor.execute('BEGIN')

  def rollback(self):
    self.connection.rollback()

  def sql(self, sql, *binds, **kwargs):
    sql = sql.format(
      bind_char = self.bind_char,
      **kwargs
    )
    print sql, binds
    return self.cursor.execute(sql, binds)

  def column_sql(self, name, data_type, args = None):
    if args is None: args = {}

    sql = [name, self.get_type_sql(data_type, **args)]
    if 'constraints' in args:
      sql += self.constraints_sql(**args)
    return ' '.join(sql)

  def constraints_sql(self, **options):
      return [self.get_type_sql(k, **options) for k in options['constraints']]

  def get_type_sql(self, name, **args):
    return getattr(self, name + '_sql')(**args)

  def string_sql(self, *args, **kwargs):
    length = kwargs['length'] if 'length' in kwargs else 20
    return 'VARCHAR({length})'.format(length = length)

  def integer_sql(self, *args, **kwargs):
    return 'INTEGER'

  def unique_sql(self, *args, **kwargs):
    return 'UNIQUE'

  def datetime_sql(self, *args, **kwargs):
    return 'TIMESTAMP'
