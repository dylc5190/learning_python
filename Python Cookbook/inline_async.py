# Example of implementing an inlined-callback function

# Sample function to illustrate callback control flow

def apply_async(func, args, *, callback):
    # Compute the result
    result = func(*args)

    # Invoke the callback with the result
    callback(result)

# Inlined callback implementation
from queue import Queue
from functools import wraps

class Async:
    def __init__(self, func, args):
        self.func = func
        self.args = args

def inlined_async(func):
    @wraps(func)
    def wrapper(*args):
        f = func(*args) # f is <generator object test at 0x000001C6B20A4EC8>
        result_queue = Queue()
        result_queue.put(None) # the first value sent to a generator has to be None.
        while True:
            result = result_queue.get()
            try:
                '''
                result will be sent to r in test()
                a will be the Async object yield from test()
                '''
                a = f.send(result)
                apply_async(a.func, a.args, callback=result_queue.put)
            except StopIteration:
                break
    return wrapper

# Sample use
def add(x, y):
    return x + y

@inlined_async
def test():
    r = yield Async(add, (2, 3))
    print(r) # will be 5
    r = yield Async(add, ('hello', 'world'))
    print(r) # will be 'helloworld'
    for n in range(10):
        r = yield Async(add, (n, n))
        print(r)
    print('Goodbye')

if __name__ == '__main__':
    # Simple test
    print('# --- Simple test')
    test() # calling test() should return a generator but here it's wrapped by inlined_async and therefore wrapper() is invoked.

    print('# --- Multiprocessing test')
    import multiprocessing
    pool = multiprocessing.Pool()
    apply_async = pool.apply_async
    test()
