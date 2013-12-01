
def pytest_addoption(parser):
    parser.addoption("--db",
      action = "store",
      default = "sqlite",
      help = "what db backend to test"
    )
