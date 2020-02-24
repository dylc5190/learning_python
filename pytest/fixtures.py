import pdb
import pytest

class Foo():
    def __init__(self,n=0):    
        print("Init Foo")
        self.id = n
    def foo(self):
        print("foo")

# you can reference another fixture that has been initiated
# request.seesion gives you the pytest session object

@pytest.fixture(scope='session')
def sess_ft_2(request,sess_ft_1):
    print("sess_ft_2 autouse=False")
    print("sess_ft_2 id={}".format(id(sess_ft_1)))
    return sess_ft_1

@pytest.fixture(scope='session')
def sess_ft_4(request):
    print("sess_ft_4 autouse=False")
    foo = Foo(4)
    print("sess_ft_4 id={}".format(id(foo)))
    return foo

# the running order of session fixtures with autouse enabled seems to be sorted by name
# cannot find a way to reorder. maybe just consolidate them in 1 fixture.

@pytest.fixture(scope="session", autouse=True)
def sess_ft_3(request):
    print("sess_ft_3 autouse=True")

# sess_ft_4 is not autouse but here it will be called before sess_ft_1

@pytest.fixture(scope="session", autouse=True)
def sess_ft_1(request,sess_ft_4):
    print("sess_ft_1 autouse=True")
    foo = Foo(1)
    print("sess_ft_1 id={}".format(id(foo)))
    print("sess_ft_4 id={}".format(id(sess_ft_4)))
    return foo




