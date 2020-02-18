import operator

class StructTupleMeta(type):
    def __init__(cls, *args, **kwargs):
        print('StructTupleMeta __init__')
        print(cls, *args, **kwargs)
        super().__init__(*args, **kwargs)
        for n, name in enumerate(cls._fields_):
            setattr(cls, name, property(operator.itemgetter(n)))

class StructTuple(tuple, metaclass=StructTupleMeta):
    _fields_ = []
    def __new__(cls, *args):
        print('StructTuple __new__')
        if len(args) != len(cls._fields_):
            raise ValueError('{} arguments required'.format(len(cls._fields_)))
        return super().__new__(cls,args)

# Examples
class Stock(StructTuple):
    _fields_ = ['name', 'shares', 'price']

class Point(StructTuple):
    _fields_ = ['x', 'y']

print('main')
s = Stock('ACME', 50, 91.1)