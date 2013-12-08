import pytest
import sys

def run_test(db, *args):
  print '***Running all Models tests with ' + db + '***'
  pytest.main(list(args) + ['--db', db, 'models'])

if __name__ == '__main__':
  args = []
  dbs = ['mysql', 'sqlite', 'postgres']
  if len(sys.argv) > 1:
    for v in sys.argv[1:]:
      if v == 'verbose':
        args = ['-s'] + args
      elif not v == 'all':
        dbs = [v]

  for db in dbs:
    run_test(db, *args)
