from functools import partial

def transform_column(column):
  name = column[0]
  data_type = column[1]
  args = column[2] if len(column) == 3 else {}
  return (name, data_type, args)

def commit_after(func):
  def wrapper(self, *args, **kwargs):
    try:
      return func(self, *args, **kwargs)
    finally:
      print 'Commiting'
      self.commit()
  return wrapper

class Base(object):
  bind_char = '%s'
  def __init__(self, *args, **kwargs):
    self.connect(*args, **kwargs)

  def quote_if_needed(self, v):
    return v

  def commit(self):
    self.connection.commit()

  def start_transaction(self):
    print 'Transaction Started'
    self.cursor.execute('BEGIN')

  def rollback(self):
    print 'Rolling Back'
    self.connection.rollback()

  def get_cursor(self):
    return self.connection.cursor()

  def sql(self, sql, *binds, **kwargs):
    cursor = kwargs.pop('cursor', self.cursor)

    sql = sql.format(
      bind_char = self.bind_char,
      **kwargs
    )

    print sql, binds, cursor
    cursor.execute(sql, binds)
    return cursor


class Connection(Base):
  select_sql = 'SELECT {select} FROM {table_name} WHERE {column} = {bind_char}'
  delete_sql = 'DELETE FROM {table_name} WHERE {column} = {bind_char}'
  insert_sql = 'INSERT INTO {table_name} ({columns}) VALUES ({values})'
  update_sql = 'UPDATE {table_name} SET {columns} WHERE id = {bind_char}'
  limit_sql = 'LIMIT {limit}'
  order_by_sql = 'ORDER BY {order_by}'
  offset_sql = 'OFFSET {offset}'

  def select(self, *args, **kwargs):
    return Query(self, *args, **kwargs)

  def count(self, table_name, column, value, **kwargs):
    sql = self.get_select_sql(**kwargs)
    cursor = self.sql(sql, value,
      table_name = table_name,
      column = column,
      select = 'count(*) count',
      **kwargs
    )

    return self.get_count(cursor)

  def get_count(self, cursor):
    return cursor.fetchone()['count']

  def get_select_sql(self, **kwargs):
    return ' '.join([
      self.select_sql,
      self.get_select_modifiers_sql(**kwargs)
    ])

  def get_select_modifiers_sql(self, **kwargs):
    modifiers = []
    for m in ('order_by', 'limit', 'offset'):
      if kwargs.get(m, None):
        modifiers.append(getattr(self, m + '_sql'))
    return ' '.join(modifiers)

  @commit_after
  def delete(self, table_name, column, value):
    self.sql(self.delete_sql, value,
      column = self.quote_if_needed(column),
      table_name = table_name
    )

  @commit_after
  def insert(self, table_name, return_id = False, **data):
    columns = map(self.quote_if_needed, data.keys())
    values = data.values()
    self.sql(self.get_insert_sql(return_id), *values,
      table_name = table_name,
      columns = ", ".join(columns),
      values = ", ".join([self.bind_char for x in columns])
    )

    if return_id:
      return self.last_row_id()

  def get_insert_sql(self, return_id):
    return self.insert_sql

  def last_row_id(self):
    return self.cursor.lastrowid

  @commit_after
  def update(self, table_name, id, **data):
    columns = ", ".join([ c + ' = {bind_char}' for c in data])
    binds = data.values() + [id]
    self.sql(self.update_sql, *binds,
      table_name = table_name,
      columns = columns.format(bind_char = self.bind_char)
    )


class TableManager(Base):
  create_sql = 'CREATE TABLE {table_name} ({columns})'
  drop_table_sql = 'DROP TABLE IF EXISTS {table_name}'
  index_sql = 'CREATE INDEX {index_name} ON {table_name} ({column_name})'
  def __init__(self, connection, cursor):
    self.connection = connection
    self.cursor = cursor

  @commit_after
  def create_table(self, table_name, *columns):
    columns = map(transform_column, columns)
    sql = [self.column_sql(*c) for c in columns]
    sql += self.table_constraints_sql(*columns)
    self.sql(self.create_sql,
      table_name =  table_name,
      columns = ", ".join(filter(bool, sql)),
    )
    self.create_indexes(table_name, columns)

  @commit_after
  def create_indexes(self, table_name, columns):
    indexed_columns = [c for c in columns if c[2].get('indexed', None)]
    for c in indexed_columns:
      self.create_index(table_name, c)

  @commit_after
  def create_index(self, table_name, column):
    self.sql(self.index_sql,
      table_name = self.quote_if_needed(table_name),
      column_name = column[0],
      index_name = '_'.join([table_name, column[0], 'index'])
    )

  @commit_after
  def drop_table(self, table_name):
    self.sql(self.drop_table_sql, table_name = table_name)

  def column_sql(self, name, data_type, args = None):
    if args is None: args = {}

    sql = [
      self.quote_if_needed(name),
      self.get_sql(data_type, **args)
    ] + self.column_constraints_sql(**args)

    return ' '.join([x for x in sql if x])


  def table_constraints_sql(self, *columns):
    output = []
    for c in columns:
      if len(c) > 2 and\
          'foreign_key' in c[2] and\
            c[2]['foreign_key']:
        sql = self.foreign_key_table_sql(*c)
        output.append(sql)
      if c[1] == 'primary_key':
        output.append(self.primary_key_table_sql(c[0]))
    return output

  def primary_key_table_sql(self, column_name):
    return None

  def column_constraints_sql(self, **options):
      return [self.get_sql(k, **options) for k in options if options[k]]

  def get_sql(self, name, **args):
    f = getattr(self, name + '_sql', None)
    if f:
      return f(**args)
    else:
      return ''

  def string_sql(self, *args, **kwargs):
    length = kwargs.get('length', 20)
    return 'VARCHAR({length})'.format(length = length)

  def integer_sql(self, *args, **kwargs):
    return 'INTEGER'

  def boolean_sql(self, *args, **kwargs):
    return 'BOOLEAN'

  def not_null_sql(self, *args, **kwargs):
    return 'NOT NULL'

  def unique_sql(self, *args, **kwargs):
    return 'UNIQUE'

  def datetime_sql(self, *args, **kwargs):
    return 'TIMESTAMP'

  def foreign_key_table_sql(self, column_name, colum_type, args) :
    table_name, foreign_name = args['foreign_key']
    column_name = self.quote_if_needed(column_name)
    return '''
      FOREIGN KEY
        ({column_name})
      REFERENCES
        {table_name}({foreign_name})
      '''.format(
      column_name = column_name,
      table_name = table_name,
      foreign_name = foreign_name
    )

class Query(object):
  def __init__(self, db, *args, **kwargs):
    self.db = db
    self.select_params = args
    self.select_modifiers = kwargs

  @property
  def first(self):
    return self.select(limit = 1).fetchone()

  @property
  def count(self):
    limit = self.select_modifiers.get('limit', None)
    return self.db.count(*self.select_params, limit = limit)

  @property
  def all(self):
    return self.select().fetchall()

  def paginate(self, page_size, page_number = 0):
    return self.select(
      limit = page_size,
      offset = page_size * page_number
    ).fetchall()

  def get_select_modifiers(self, **kwargs):
    modifiers = self.select_modifiers.copy()
    modifiers.update(kwargs)
    for k,v in modifiers.items():
      if v is None:
        del modifiers[k]
    return modifiers

  def select(self, select = '*', **kwargs):
    table_name, column, value = self.select_params
    modifiers = self.get_select_modifiers(**kwargs)
    sql = self.db.get_select_sql(**modifiers)
    return self.db.sql(sql, value,
      cursor = self.db.get_cursor(),
      column = self.db.quote_if_needed(column),
      select = select,
      table_name = table_name,
      **modifiers
    )
