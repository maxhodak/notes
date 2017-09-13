import os
import errno

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST:
      pass
    else: raise

def touch(fname, times = None):
  with file(fname, 'a'):
    os.utime(fname, times)
