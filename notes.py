#!/usr/bin/env python
# encoding: utf-8
"""
A Python script for keeping track of Markdown-based notes.
"""

import sys
import os
import time
import errno
import json
import subprocess
import tempfile
import getpass
import marshal
import random
import datetime
import base64
import argparse



def edit_note2(fname, key, command = ["atom", "--wait"]):
  file_exists = os.path.isfile(fname)
  touch(fname)

  try:
    if file_exists is True:
      with open(fname, 'r') as f:
        data = json.load(f)
        plaintext = decrypt(data['data'], data['salt'], key['decrypt_key'])
      with open(fname, 'w') as f:
          f.write(plaintext)
  except ValueError, err:
    print "Error: %s" % str(err)
    return False

  subprocess.call(command + [fname])

  with open(fname, 'r') as fd:
    salt, ciphertext = encrypt(key['decrypt_key'], fd.read())
  with open(fname, 'wb') as fd:
    json.dumps({
        "salt": salt,
        "data": ciphertext
    }, fd)

  return True

def edit_note(fname = None, command = ["atom", "--wait"]):
  password = getpass.getpass("Password: ")

  file_exists = os.path.isfile(fname)
  touch(fname)

  try:
    if file_exists is True:
      with open(fname, 'r') as f:
        data = marshal.load(f)
        if not data.startswith("!ENC%"):
          raise ValueError("Invalid file header!  Are you sure this file is encrypted?")
        plaintext = decrypt(data[21:], data[5:21], password)
        if not plaintext.startswith("$aes256$"):
          raise ValueError("Invalid encryption password!")
      with open(fname, 'w') as f:
          f.write(plaintext[8:])
  except ValueError, err:
    print "Error: %s" % str(err)
    return False

  subprocess.call(command + [fname])

  with open(fname, 'r') as fd:
    data = "$aes256$" + fd.read()
    salt, ciphertext = encrypt(password, data)
  with open(fname, 'wb') as fd:
    marshal.dump("!ENC%" + salt + ciphertext, fd)

  return True

def find_note_by_name(name):
  results = subprocess.Popen(["find", notespath, "-name", '%s.mdown' % name], stdout = subprocess.PIPE).communicate()[0]
  results = results[:-1].split("\n")
  ret = []
  if results == ['']: return (False, False)
  for result in results:
    try:
      fd = open(result, 'rb')
      data = marshal.load(fd)
      if data.startswith("!ENC%"):
        ret.append((result, True))
      else:
        ret.append((result, False))
      fd.close()
    except ValueError:
      ret.append((result, False))
  if len(ret) > 1:
    print "Multiple matches for %s found:" % name
    print "  idx\tenc\tName"
    for r in range(len(ret)):
      print "   %d\t%s\t%s" % (r, str(ret[r][1]), ret[r][0])
    print ""
    selection = raw_input("  Select an index: ")
    print ""
    return ret[int(selection)]
  return ret[0]

def display_help(argv = sys.argv):
  print "  Editor is %s, pager is %s." % (os.getenv('EDITOR'), os.getenv('PAGER'))
  print ""
  print "  Usage: %s [COMMAND]" % argv[0]
  print ""
  print "  Commands:"
  print "    new <title>            Create a new note named <title> and open it in $EDITOR."
  print "    cat <title>            Display the content of <title> in $PAGER."
  print "    search <query>         Full text search for <query> in your notes tree."
  print "    list [-a]              List all titles in your notes tree. Optional flag -a prints full paths."
  print "    edit <title>           Open the note named <title> in $EDITOR."
  print "    journal                Create a new note with today's date as the title."
  print "    scratch                Open the scratch pad."
  print ""
  print "    stack                  View the current micronote stack.  Short form: s."
  print "    push <unote>           Push a micronote onto the active stack."
  print "    pop <idx>              Unset the micronote at position idx."
  print ""
  print "    git-init               Initialize version control in your notes tree."
  print "    git-commit             Commit the current state of your notes tree to version control."
  print "    git-log                View your version control commit log in $PAGER."
  print "    git-status             See the status of your notes tree with respect to unversioned changes."
  print ""
  print "    help                   Display this help message and quit."
  print ""
  print " Optional arguments:"
  print "    -a                     Print full paths.  Valid for: list."
  print "    -x                     Use legacy file format and encryption."
  print ""
  print "  Notes is maintained by Max Hodak <maxhodak@gmail.com>.  Please report issues at http://github.com/maxhodak/notes/issues/."

def main(argv = None):
  if argv is None:
    argv = normalize_argv(sys.argv)

  if len(argv) < 2:
    display_help()
    sys.exit(2)

  key = keyfile_read(notespath)

  elif argv[1] == 'scratch':
    edit_note2("%s/.scratch.mdown" % (notespath,), key)

  elif argv[1] == 'cat':
    (fname, encrypted) = find_note_by_name(argv[2])
    if fname is False:
      print "Error: Object by name %s not found." % argv[2]
    else:
      if encrypted:
          edit_note(fname, command = ['less'])
      else:
        os.system("$PAGER %s" % fname)

  elif argv[1] == 'edit':
    (fname, encrypted) = find_note_by_name(argv[2])
    if fname is False:
      print "Error: Object by name %s not found." % argv[2]
    else:
      if encrypted:
          edit_note(fname)
      else:
        os.system("$EDITOR %s" % fname)

  elif argv[1] == 'list':
    if len(argv) > 2:
      if argv[2] == '-a':
        os.system("find %s/2* -name '*.mdown'" % notespath)
      else:
        print "Invalid flag: %s" % argv[2]
    else:
      os.system("find %s/2* -name '*.mdown' | cut -d '/' -f 9 | cut -d '.' -f 1" % notespath)

  elif argv[1] == 'delete':
    (fname, enc) = find_note_by_name(argv[2])
    if fname is False:
      print "Error: Object by name %s not found." % argv[2]
    else:
      check = raw_input("Delete %s: Are you sure? [y/N] " % fname)
      if check in ("y","Y"):
        try:
          os.system("rm %s" % fname)
        except IOError, err:
          print "Error: %s", str(err)

  else:
    display_help()

if __name__ == "__main__":
  sys.exit(main())
