from test_model import Base
from models.user import User

class TestUser(Base):
  def setup(self):
    User.drop_table()
    User.init_table()

  def test_by_username(self):
    User.create(
      username = 'bob.barker',
      email = 'bob@barker.com',
      password = 'password'
    )

    result = User.find_by_username('bob.barker')
    assert result.email == 'bob@barker.com'

