import pdb
import pytest
from fixtures import *

# fixtures can be placed in an individual file

class Bar():
    def __init__(self):
        print("Init Bar")
    def bar(self):
        print("bar")

def pytest_addoption(parser):
    parser.addoption('--xyz', action='store', default='zoo')

def pytest_sessionstart(session):    
    print("pytest_sessionstart")
    print(session.config.option.xyz)
    pdb.set_trace()
    pytest.na_tool = Bar()

def pytest_pyfunc_call(pyfuncitem):
    print("pytest_pyfunc_call")