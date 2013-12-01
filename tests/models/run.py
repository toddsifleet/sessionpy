import pytest
import sys

def run_test(db):
  print '***Running all Models tests with ' + db + '***'
  pytest.main(['--db', db, 'models'])

if __name__ == '__main__':
  db = sys.argv[1]

  if db  == 'all':
    for db in ['mysql', 'sqlite', 'postgres']:
      run_test(db)
  else:
    run_test(db)
