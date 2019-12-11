import pdb

class IterA:
  def __iter__(self):
    print(">>> iter")
    return self

class IterB:
  def __iter__(self):
    print(">>> iter")
    return self

  def __next__(self):
    print('>>> next')

class IterC:
  def __iter__(self):
    print(">>> iter")
    return [1,2,3,4]

class IterD:
  def __iter__(self):
    print(">>> iter")
    return iter([1,2,3,4])

class IterE:
  def __iter__(self):
    print(">>> iter")
    for i in range(5):
      print("yield {}".format(i))
      yield i

if __name__ == '__main__':

  print('''
  x = IterA()
  # Either next() or for will raise exception because IterA does not implement __next
  y=next(x)
  [y for y in x]
  ''')
  pdb.set_trace()

  print('''
  x = IterB()
  # next() call __next__ directly
  y=next(x)
  y=next(x)
  # The following for loop becomes infinite because IterB does not implement StopIteration exception.
  # Note __iter__ is called first then __next__. You may need to scroll up very far to find it.
  [y for y in x]
  ''')
  pdb.set_trace()

  print('''
  x=IterC()
  # next() raises exception because __next__ is not implemented
  y=next(x)
  for is ok because __iter__ does not return a iterator
  [v for v in x]
  ''')
  pdb.set_trace()

  print('''
  x=IterD()
  # next() raises exception because __next__ is not implemented
  y=next(x)
  # for is ok because __iter__ returns an iterator (not itself)
  [v for v in x]
  ''')
  pdb.set_trace()

  print('''
  x=IterE()
  # next() raises exception because __next__ is not implemented 
  y=next(x)
  # for is ok because __iter__ returns a generator
  [v for v in x]
  ''')
  pdb.set_trace()
