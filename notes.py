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

def display_help():
  print "  Valid commands:"
  print "    new <title>      Create a new note named <title> and open it in $EDITOR."
  print "    search <query>   Full text search for <query> in your notes tree."
  print "    list             List all titles in your notes tree."
  print "    edit <title>     Open the note titled <title> in $EDITOR."
  print "    git-init         (Re-)Initialize version control in your notes tree."
  print "    git-add          Add all untracked notes to version control."
  print "    git-commit       Commit the current state of your notes tree to version control."
  print "    help             Display this help message and quit."

def main(argv=None):
  if argv is None:
    argv = normalize_argv(sys.argv)
  
  if len(argv) < 2:
    display_help()
    sys.exit(2)
  
  if argv[1] == 'new':
    path = "/Users/maxhodak/Documents/Notes/%s" % time.strftime("%Y/%m/%d")
    mkdir_p(path)
    os.system("$EDITOR %s/%s.mdown" % (path, argv[2]))
  
  elif argv[1] == 'search':
    os.system("grep -ir '%s' ~/Documents/Notes*" % argv[2])
  
  elif argv[1] == 'list':
    os.system("find ~/Documents/Notes -name '*.mdown' | cut -d '/' -f 9 | cut -d '.' -f 1")
  
  elif argv[1] == 'edit':
    os.system("find ~/Documents/Notes -name '%s.mdown' -exec $EDITOR '{}' \;" % argv[2])
  
  elif argv[1] == 'git-init':
    os.system("echo '.DS_Store' > ~/Documents/Notes/.gitignore")
    os.system("git init ~/Documents/Notes")
  
  elif argv[1] == 'git-add':
    os.system("cd /Users/maxhodak/Documents/Notes && git add *")
  
  elif argv[1] == 'git-commit':
    os.system("cd /Users/maxhodak/Documents/Notes && git commit -a")
  
  elif argv[1] == 'help':
    display_help()
  
  else:
    display_help()

if __name__ == "__main__":
  sys.exit(main())