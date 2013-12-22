from bottle import route, run, template, hook, request, redirect

import sys
base_path = '/Users/toddsifleet/Dropbox/github/sessionpy/'
sys.path.append(base_path + 'sessionpy')
from authenticator import Authenticator
from models.admin import AdminUser, AdminSession

skip_auth_check = [
  '/login'
]

def load_authenticator():
  return Authenticator(base_path + 'tests/models/mysql.config')

@hook('before_request')
def authenticate(*args, **kwargs):
  if request.path in skip_auth_check:
    request.current_user = None
    return
  redirect(request.path + 'god')

@route('/')
def index():
  return 'index'

@route('/page')
def page():
  return 'page'

@route('/login')
def login():
  if 'login' in request.query:
    username_or_email = request.query.get('username_or_email', None)
    password = request.query.get('password', None)
    print username_or_email, password
    if username_or_email and password:
      user =  AdminUser.login(
        request.query['username_or_email'],
        request.query['password']
      )
      if user:
        redirect('/admin')
  return 'login'


authenticator = load_authenticator()
AdminUser.drop_table()
AdminUser.init_table()
AdminUser.create(
  username = 'todd',
  password = 'tim'
)

run(
  host = 'localhost',
  port = 8081,
  reloader = True
)

