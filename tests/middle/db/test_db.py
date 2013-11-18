from tests import base

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
    self.db.create_table('test_table', 'c1', 'c2', 'c3')

  def teardown(cls):
    pass

  def test_select(self):
    result = self.db.select('test_table', 'c1', 'c1-v0')
    assert result == None

    self.insert_dummy_row()

    result = self.db.select('test_table', 'c1', 'c1-v0')
    assert result[2] == 'c2-v0'

  def test_insert(self):
    result = self.db.select('test_table', 'c1', 'c1-v0')
    assert result == None

    id = self.db.insert('test_table',
      c1 = 'v1',
      c2 = 'v2'
    )

    result = self.db.select('test_table', 'id', id)
    assert result[2] == 'v2'

  def test_update(self):
    id = self.insert_dummy_row()
    self.db.update('test_table', id,  c1 = 'c1-update')
    result = self.db.select('test_table', 'id', id)
    assert result[1] == 'c1-update'

  def test_delete(self):
    id = self.insert_dummy_row()
    self.db.delete('test_table', id)
    result = self.db.select('test_table', 'id', id)
    assert result is None

  def insert_dummy_rows(self, count = 10):
    return map(dummy_row, range(count))

  def insert_dummy_row(self, n = 0):
    return self.db.insert('test_table',
      c1 = 'c1-v{0}'.format(n),
      c2 = 'c2-v{0}'.format(n),
      c3 = 'c3-v{0}'.format(n)
    )
