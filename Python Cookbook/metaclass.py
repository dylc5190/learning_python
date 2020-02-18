class Meta(type):
    def __new__(cls,name,bases,dct):
        print('meta new')
        print(cls,name,bases,dct)
        return super().__new__(cls,name,bases,dct)
    def __init__(*args, **kwargs):
        print('meta init')
        print(*args, **kwargs)
    def __call__(*args, **kwargs):
        print('meta call')
        print(*args, **kwargs)

class A(metaclass=Meta):    # invoke Meta.__new__ and Meta.__init__
    pass                    # __new__ is called before creating the class and __init__ is called after class is created.
                            # if you want to change class definition you might use __new__.
                            # if you need to access class attributes, you might use __init__.

print('a=A()')
a=A()                       # invoke Meta.__call__
print('b=A()')
b=A()                       # invoke Meta.__call__