class Node:
 def __init__(self, value):
  self._value = value
  self._children = []

 def __repr__(self):
  return 'Node({!r})'.format(self._value)

 def add_child(self, node):
  self._children.append(node)

 def __iter__(self):
  print(">>>> __iter__") 
  return iter(self._children)

 def depth_first(self):
  print(">>>> depth_first 1")
  yield self
  print(">>>> depth_first 2")
  for c in self:
   print(">>>> depth_first 3")
   yield from c.depth_first()

a=Node(0)
a1=Node(1)
a2=Node(2)
a11=Node(11)
a.add_child(a1)
a.add_child(a2)
a1.add_child(a11)

for ch in a:
 print(ch)

print(">>>> test depth_first")

for ch in a.depth_first():
 print(ch)
