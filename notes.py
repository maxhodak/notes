#!/usr/bin/env python
# encoding: utf-8
"""
A Python script for keeping track of Markdown-based notes.
"""

import sys, os, time, errno, json, subprocess, tempfile, getpass, marshal, random, datetime, base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

notespath = os.getenv("NOTESPATH")
if notespath is None:
  if sys.platform in ("darwin"):
    notespath = "/Users/%s/Documents/Notes" % os.getlogin()
  elif sys.platform in ("linux2"):
    notespath = "/home/%s/notes" % os.getlogin()
  else:
    print "Platform not recognized and $NOTESPATH not set.  Please set $NOTESPATH first."
    sys.exit(2)
  os.system("touch %s/.notestack" % notespath)
  print "$NOTESPATH not set; using default of %s" % notespath
  print "You should add `export NOTESPATH=%s` (or otherwise) to your shell profile." % notespath

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

def normalize_argv(argv):
  if argv[0] is 'python':
    argv.remove(0)
  return argv

def encrypt(password, text):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    return (salt, f.encrypt(bytes(text)))

def decrypt(ciphertext, salt, password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    return f.decrypt(ciphertext)

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
  print "  Valid commands:"
  print "    new <title> [-e]       Create a new note named <title> and open it in $EDITOR."
  print "    cat <title>            Display the content of <title> in $PAGER."
  print "    search <query>         Full text search for <query> in your notes tree."
  print "    list [-a]              List all titles in your notes tree. Optional flag -a prints full paths."
  print "    edit <title>           Open the note named <title> in $EDITOR."
  print "    journal                Create a new note with today's date as the title."
  print ""
  print "    stack                  View the current micronote stack.  Short form: s."
  print "    push <unote>           Push a micronote onto the active stack."
  print "    pop <idx>              Unset the micronote at position idx."
  print ""
  print "    git-init               (Re-)Initialize version control in your notes tree."
  print "    git-commit             Commit the current state of your notes tree to version control."
  print "    git-log                View your version control commit log in $PAGER."
  print "    git-status             See the status of your notes tree with respect to unversioned changes."
  print ""
  print "    help                   Display this help message and quit."
  print ""
  print " Optional arguments:"
  print "    -e                     Encrypt using AES-256 with a 256 bit key.  Valid for: new."
  print "    -a                     Print full paths.  Valid for: list."
  print ""
  print "  Notes is maintained by Max Hodak <maxhodak@gmail.com>.  Please report issues at http://github.com/maxhodak/notes/issues/."

def load_stack(notespath):
  try:
    return json.load(open("%s/.notestack" % notespath, 'r+'))
  except ValueError:
    return []

def save_stack(notespath, stack = []):
  return json.dump(stack, open("%s/.notestack" % notespath, 'w'))

def main(argv = None):
  if argv is None:
    argv = normalize_argv(sys.argv)

  if len(argv) < 2:
    display_help()
    sys.exit(2)

  if argv[1] in ('stack', 's'):
    stack = load_stack(notespath)
    for i in xrange(len(stack)):
      print " ==> [%i] %s" % (i, stack[i])

  elif argv[1] == 'push':
    stack = load_stack(notespath)
    stack.append(" ".join(argv[2:]))
    save_stack(notespath, stack)

  elif argv[1] == 'pop':
    stack = load_stack(notespath)
    if len(argv) == 2:
      print " ==> %s" % (stack[-1], )
      del stack[-1]
      save_stack(notespath, stack)
    elif int(argv[2]) >= 0 and int(argv[2]) < len(stack):
      del stack[int(argv[2])]
      save_stack(notespath, stack)
    else:
      print "Error!"

  elif argv[1] == 'journal':
    path = "%s/%s" % (notespath, time.strftime("%Y/%m/%d"))
    mkdir_p(path)
    edit_note("%s/%s.mdown" % (path, time.strftime("%Y-%m-%d")))

  elif argv[1] == 'new':
    path = "%s/%s" % (notespath,time.strftime("%Y/%m/%d"))
    mkdir_p(path)
    edit_note("%s/%s.mdown" % (path, argv[3]))

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

  elif argv[1] == 'search':
    os.system("grep -ir '%s' %s*" % (argv[2], notespath))

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

  elif argv[1] == 'git-init':
    mkdir_p(notespath)
    os.system("echo '.DS_Store' > %s/.gitignore" % notespath)
    os.system("cd %s && git init ." % notespath)

  elif argv[1] == 'git-log':
    os.system("cd %s && git log" % notespath)

  elif argv[1] == 'git-status':
    os.system("cd %s && git status -uall" % notespath)

  elif argv[1] == 'git-commit':
    os.system("cd %s && git status --porcelain -uall | grep '^??' | cut -d' ' -f2 | xargs git add" % \
                notespath)
    commit_msg = raw_input("Commit log message: ")
    os.system("cd %s && git commit -am '%s'" % (notespath, commit_msg))

  else:
    display_help()

if __name__ == "__main__":
  sys.exit(main())
