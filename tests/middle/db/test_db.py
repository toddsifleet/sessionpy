from tests import base
import datetime

class Base(object):
  @classmethod
  def setup_class(cls):
    cls.db = cls.connect()

  @classmethod
  def teardown_class(cls):
    cls.disconnect()

  @classmethod
  def disconnect(cls):
    pass

  def setup(self):
    self.db.drop_table('test_table')
    self.db.create_table('test_table',
      ('c1', 'string'),
      ('c2', 'integer'),
      ('c3', 'datetime')
    )

  def teardown(cls):
    pass

  def test_select(self):
    time = datetime.datetime.today().replace(microsecond=0)
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
    self.db.update('test_table', id,  c1 = 'updated_test_string')
    result = self.db.select('test_table', 'id', id)
    assert result['c1'] == 'updated_test_string'

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
      'c3': datetime.datetime.today()
    }

    vals.update(kwargs)
    return self.db.insert('test_table',  **vals)
