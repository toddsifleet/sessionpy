from tests import test_utils
import pytest

class Base(object):
  @classmethod
  def setup_class(cls):
    cls.db = cls.connect()
    cls.table_manager = cls.db.table_manager

  @classmethod
  def teardown_class(cls):
    cls.disconnect()

  @classmethod
  def disconnect(cls):
    cls.db.commit()

  def insert_dummy_row(self, n = 0, **kwargs):
    vals = {
      'c1': 'test_string',
      'c2': 1234,
      'c3': test_utils.now()
    }

    vals.update(kwargs)
    return self.db.insert('test_table',  **vals)

  def drop_table(self, table_name):
    self.table_manager.drop_table(table_name)

  def create_test_table(self):
    self.drop_table('test_child_table')
    self.drop_table('test_table')
    self.table_manager.create_table('test_table',
      ('c1', 'string'),
      ('c2', 'integer'),
      ('c3', 'datetime')
    )

class Query(Base):
  def setup(self):
    self.create_test_table()

  def teardown(cls):
    pass

  def test_select(self):
    time = test_utils.now()
    row = self.insert_dummy_row(c3 = time)

    result = self.db.select('test_table', 'c1', 'test_string')
    assert result['c1'] == 'test_string'
    assert result['c2'] == 1234
    assert result['c3'] == time

  def test_insert(self):
    id = self.db.insert('test_table',
      c1 = 'v1',
      c2 = 2
    )

    result = self.db.select('test_table', 'id', id)
    assert result['c1'] == 'v1'

  def test_update(self):
    id = self.insert_dummy_row()
    self.db.update('test_table', id,  c1 = 'test_string_2')
    result = self.db.select('test_table', 'id', id)
    assert result['c1'] == 'test_string_2'

  def test_delete(self):
    id = self.insert_dummy_row()
    self.db.delete('test_table', id)
    result = self.db.select('test_table', 'id', id)
    assert result is None

  def insert_dummy_rows(self, count = 10):
    return map(dummy_row, range(count))


class Constraints(Base):
  def setup(self):
    self.drop_table('test_table')

  def test_length_of_string(self):
    self.table_manager.create_table('test_table',
      ('c1', 'string', {'length': 15}),
      ('c2', 'string'),
      ('c3', 'string')
    )
    with pytest.raises(Exception):
      self.insert_dummy_row(c1 = 'A' * 16)
    self.db.commit()

  def test_unique(self):
    self.table_manager.create_table('test_table',
      ('c1', 'string', {'unique': True}),
      ('c2', 'string'),
      ('c3', 'string')
    )
    self.insert_dummy_row()
    with pytest.raises(Exception):
      self.insert_dummy_row()
    self.db.commit()

  def test_foreign_key(self):
    self.create_test_table()
    id_1 = self.insert_dummy_row()

    self.drop_table('test_child_table')
    self.table_manager.create_table('test_child_table',
      ('c1', 'integer', {'foreign_key': ('test_table', 'id')}),
      ('c2', 'string')
    )

    def dummy_row(id = 1235):
      self.db.insert('test_child_table',
        c1 = id,
        c2 = 'test_string'
      )
    dummy_row(id_1)

    with pytest.raises(Exception):
      dummy_row()

    self.table_manager.commit()
    self.drop_table('test_child_table')
    self.drop_table('test_table')
    self.table_manager.commit()

