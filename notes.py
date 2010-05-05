#!/usr/bin/env python
# encoding: utf-8
"""
A Python script for keeping track of Markdown-based notes.
"""

import sys, os, time, errno

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
  print "  Editor is %s, pager is %s." % (os.getenv('EDITOR'), os.getenv('PAGER'))
  print "  Valid commands:"
  print "    new <title>      Create a new note named <title> and open it in $EDITOR."
  print "    search <query>   Full text search for <query> in your notes tree."
  print "    list [-all]      List all titles in your notes tree. Optional flag -all prints full paths."
  print "    edit <title>     Open the note named <title> in $EDITOR."
  print "    git-init         (Re-)Initialize version control in your notes tree."
  print "    git-add          Add all untracked notes to version control."
  print "    git-commit       Commit the current state of your notes tree to version control."
  print "    git-log          View your version control commit log in $PAGER."
  print "    git-status       See the status of your notes tree with respect to unversioned changes."
  print "    help             Display this help message and quit."
  print "  Notes is maintained by Max Hodak <max@myfit.com>.  Please report issues at http://github.com/maxhodak/notes/issues/."

def main(argv=None):
  if argv is None:
    argv = normalize_argv(sys.argv)
  
  notespath = os.getenv("NOTESPATH")
  if notespath is None:
    if sys.platform in ("darwin"):
      notespath = "/Users/%s/Documents/Notes" % os.getlogin()
    elif sys.platform in ("linux2"):
      notespath = "/home/%s/notes" % os.getlogin()
    else:
      print "Platform not recognized and $NOTESPATH not set.  Please set $NOTESPATH first."
      sys.exit(2)
    print "$NOTESPATH not set; using default of %s" % notespath
    print "You should add `export NOTESPATH=%s` (or otherwise) to your shell profile." % notespath
  
  if len(argv) < 2:
    display_help()
    sys.exit(2)
  
  if argv[1] == 'new':
    path = "%s/%s" % (notespath,time.strftime("%Y/%m/%d"))
    mkdir_p(path)
    os.system("$EDITOR %s/%s.mdown" % (path, argv[2]))
  
  elif argv[1] == 'search':
    os.system("grep -ir '%s' %s*" % (argv[2], notespath))
  
  elif argv[1] == 'list':
    if len(argv) > 2:
      if argv[2] == '-all':
        os.system("find %s -name '*.mdown'" % notespath)
      else:
        print "Invalid flag: %s" % argv[2]
    else:
      os.system("find %s -name '*.mdown' | cut -d '/' -f 9 | cut -d '.' -f 1" % notespath)
  
  elif argv[1] == 'edit':
    os.system("find %s -name '%s.mdown' -exec $EDITOR '{}' \;" % (notespath, argv[2]))
  
  elif argv[1] == 'delete':
    check = raw_input("Delete %s: Are you sure? [y/N] " % argv[2])
    if check in ("y","Y"):
      os.system("find %s -name '%s.mdown' -exec rm '{}' \;" % (notespath, argv[2]))
  
  elif argv[1] == 'git-init':
    mkdir_p(notespath)
    os.system("echo '.DS_Store' > %s/.gitignore" % notespath)
    os.system("cd %s && git init ." % notespath)
  
  elif argv[1] == 'git-add':
    os.system("cd %s && git status --porcelain -uall | grep '^??' | cut -d' ' -f2 | xargs git add" % \
                notespath)
  
  elif argv[1] == 'git-log':
    os.system("cd %s && git log" % notespath)
  
  elif argv[1] == 'git-status':
    os.system("cd %s && git status -uall" % notespath)
  
  elif argv[1] == 'git-commit':
    commit_msg = raw_input("Commit log message: ")
    os.system("cd %s && git commit -am '%s'" % (notespath, commit_msg))
  
  else:
    display_help()

if __name__ == "__main__":
  sys.exit(main())