"""Code Timer
This class is capable of timing code as a context manager or decorator.

For example:

with CodeTimer():
  for i in range(100000):
    pass

with CodeTimer('loop 1'):
  for i in range(100000):
    pass


@CodeTimer(name='test')
def decoratedFn():
  for i in range(100000):
    pass

decoratedFn()
"""

import time
from functools import wraps


class CodeTimer():
  def __init__(self, name=None):
    self.name = name
    self.start = None

  def __call__(self, f):
    @wraps(f)
    def decorated(*args, **kwds):
      with self:
        return f(*args, **kwds)
    return decorated

  def __enter__(self):
    self.start = time.time()

  def __exit__(self, excType, excValue, traceback):
    elapsedTime = str((time.time() - self.start) * 1000.0)
    if self.name:
      print('Code block %s took %s ms' % (self.name, elapsedTime))
    else:
      print('Code block took %s ms' % (elapsedTime))
