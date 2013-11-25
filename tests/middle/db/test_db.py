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
    pass

  def setup(self):
    self.table_manager.drop_table('test_table')
    self.table_manager.create_table('test_table',
      ('c1', 'string', {'length': 15}),
      ('c2', 'integer'),
      ('c3', 'datetime')
    )

  def teardown(cls):
    pass

  def test_length_of_string(self):
    with pytest.raises(Exception):
      self.insert_dummy_row(c1 = 'A' * 16)
    self.db.commit()

  def test_unique(self):
    self.table_manager.drop_table('test_table')
    self.table_manager.create_table('test_table',
      ('c1', 'string', {'constraints': ['unique']}),
      ('c2', 'string'),
      ('c3', 'string')
    )
    self.insert_dummy_row()
    with pytest.raises(Exception):
      self.insert_dummy_row()
    self.db.commit()

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

  def insert_dummy_row(self, n = 0, **kwargs):
    vals = {
      'c1': 'test_string',
      'c2': 1234,
      'c3': test_utils.now()
    }

    vals.update(kwargs)
    return self.db.insert('test_table',  **vals)
