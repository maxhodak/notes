#!/usr/bin/env python
# encoding: utf-8
"""
A Python script for keeping track of Markdown-based notes.
"""

import sys, os, time, errno, shutil, stat

def normalize_argv(argv):
  if argv[0] is 'python':
    argv.remove(0)
  return argv

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

def main(argv=None):
  if argv is None:
    argv = normalize_argv(sys.argv)
  
  if len(argv) < 2:
    sys.exit(2)
  
  if argv[1] == 'new':
    path = "~/Documents/Notes/%s" % time.strftime("%Y/%m/%d")
    mkdir_p(path)
    os.system("mate %s/%s.mdown" % (path, argv[2]))
  
  if argv[1] == 'search':
    os.system("grep -ir '%s' ~/Documents/Notes*" % argv[2])
  
  if argv[1] == 'edit':
    os.system("find ~/Documents/Notes -name '%s.mdown' -exec mate '{}' \;" % argv[2])

if __name__ == "__main__":
  sys.exit(main())