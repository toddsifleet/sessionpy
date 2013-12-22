from test_model import Base
from models.user import User

class TestUser(Base):

  def test_by_username(self):
    user = self.dummy_user()
    result = User.find_by_username('bob.barker')
    assert user == result

  def test_by_email(self):
    user = self.dummy_user()
    result = User.find_by_email('bob@barker.com')
    assert user == result

  def test_by_id(self):
    user = self.dummy_user()
    result = User.find_by_id(user.id)
    assert user == result

  def test_verify_password(self):
    user = self.dummy_user()
    result = User.find_by_id(user.id)
    assert result.verify_password('password')
    assert not result.verify_password('wrong')

  def dummy_user(self):
    return User.create(
      username = 'bob.barker',
      email = 'bob@barker.com',
      password = 'password'
    )

