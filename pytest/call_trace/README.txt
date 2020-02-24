* How is full_run.txt collected?
  1. call pdb.set_trace() in pytest_sessionstart()
  2. run pytest mytest
  3. set breakpoint
     (Pdb) b c:\program files (x86)\python37-32\lib\site-packages\pluggy\callers.py:187
     (Pdb) commands 1
     (com) import logging
     (com) logging.basicConfig(level=logging.DEBUG,filename='2.txt',filemode='a')
     (com) logger = logging.getLogger('pytest')
     (com) logger.debug('{} - {}'.format(hook_impl.function,args))
     (com) c
     (Pdb) c

* Some info during tracing. 
  > c:\program files (x86)\python37-32\lib\site-packages\_pytest\python.py(1386)__init__()
  fixtureinfo has all fixtures a test function has.
  > c:\program files (x86)\python37-32\lib\site-packages\_pytest\main.py(256)pytest_runtestloop()
  run each test case
  it calls item.config.hook.pytest_runtest_protocol(item=item, nextitem=nextitem) which calls pytest_pyfunc_call() in conftest.py if defined
  > c:\program files (x86)\python37-32\lib\site-packages\pluggy\callers.py(187)_multicall()
  test case is invoked here
  > c:\program files (x86)\python37-32\lib\site-packages\_pytest\setupplan.py(15)pytest_fixture_setup()
  when there's no fixture to run
  > c:\program files (x86)\python37-32\lib\site-packages\_pytest\fixtures.py(939)pytest_fixture_setup()
  when there's fixture to run







