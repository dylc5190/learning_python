import json

i = 0
def xyz(*params):
 global i
 for param in params:
     print(param)
     print('----')
 print('xxxx')
 i+=1
 return i

class Foo():
    def __init__(self,param):
        print(param)
        print('----')
    print('xxxx')

s = '''
{
    "a": 11,
    "b": {"b1": 21, "b2": 22},
    "c": [{"c1": 31},{"c2": 32}]
}
'''
data = json.loads(s,object_pairs_hook=xyz)
print(data)

print("====")

data = json.loads(s,object_hook=Foo)
print(data)