from tests import base

class Base(object):
  @classmethod
  def setup_class(cls):
    cls.db = cls.connect()
    cls.db.start_transaction() 

  @classmethod
  def teardown_class(cls):
    cls.db.rollback()
    cls.disconnect()
  @classmethod
  def disconnect(cls):
    pass

  def setup(self):
    self.db.drop_table('test_table')
    self.db.start_transaction()
    self.db.create_table('test_table', 'c1', 'c2', 'c3')

  def teardown(cls):
    cls.db.rollback()

  def test_select(self):
    result = self.db.select('test_table', 'c1', 'c1-v0')
    assert result == None
     
    self.insert_dummy_data(1)

    result = self.db.select('test_table', 'c1', 'c1-v0') 
    assert result[2] == 'c2-v0'

  def test_update(self):
    self.insert_dummy_data(1)
    id = self.db.select('test_table', 'c1', 'c1-v0')[0]
    self.db.update('test_table', id,  c1 = 'c1-update') 
    result = self.db.select('test_table', 'id', id)
    assert result[1] == 'c1-update'
  
  def test_delete(self):
    self.insert_dummy_data(1)
    id = self.db.select('test_table', 'c1', 'c1-v0')[0]
    self.db.delete('test_table', id)
    result = self.db.select('test_table', 'id', id)
    assert result is None

  def insert_dummy_data(self, count=10):
      [self.db.insert('test_table', 
        c1 = 'c1-v{0}'.format(n),
        c2 = 'c2-v{0}'.format(n),
        c3 = 'c3-v{0}'.format(n)
      ) for n in range(count)]
