#!/usr/bin/env python
# encoding: utf-8
"""
A Python script for keeping track of Markdown-based notes.
"""

import sys, os, time, errno, json, subprocess, tempfile, getpass, marshal, random

ENCR = True

try:
  from Crypto.Hash import SHA256
  from Crypto.Cipher import AES
except ImportError, err:
  print "PyCrypto not found, disabling cryptographic features."
  ENCR = False

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

def normalize_argv(argv):
  if argv[0] is 'python':
    argv.remove(0)
  return argv

def vim_encrypted_file(fname = None, new = False, command = 'vim', edit = True):
  key = getpass.getpass("Encryption password: ")
  key2 = SHA256.new(key)
  
  tf = tempfile.NamedTemporaryFile(mode='w', delete = False)
  
  try:
    if new is False:
      f = open(fname, 'r')
      data = marshal.load(f)
      if not data.startswith("!ENC%"):
        raise ValueError("Invalid file header!  Are you sure this file is encrypted?")
      iv = data[5:21]
      data = data[21:]
      decr_obj = AES.new(key2.digest(), AES.MODE_CBC, iv)
      plaintext = decr_obj.decrypt(data)
      if not plaintext.startswith("$aes256$"):
        raise ValueError("Invalid encryption password!")
      plaintext = plaintext[8:].rstrip("X")
      tf.write(plaintext)
      f.close()
  except ValueError, err:
    print "Error: %s" % str(err)
    return False
  
  tf.close()
  subprocess.call([command, tf.name])
  
  if edit:
    with open(tf.name) as tfd:
      data = "$aes256$" + tfd.read()
      iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
      encr_obj = AES.new(key2.digest(), AES.MODE_CBC, iv)
      ciphertext = encr_obj.encrypt(data+("X"*(16-(len(data)%16))))
      with open(fname, 'wb') as f:
        marshal.dump("!ENC%" + iv + ciphertext, f)
  
  os.unlink(tf.name)
  
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

def display_help(argv = sys.argv):
  print "  Editor is %s (secure: vim), pager is %s." % (os.getenv('EDITOR'), os.getenv('PAGER'))
  print ""
  print "  Usage: %s [COMMAND]" % argv[0]
  print ""
  print "  Valid commands:"
  print "    new <title> [-e]     Create a new note named <title> and open it in $EDITOR."
  print "    cat <title>          Display the content of <title> in $PAGER."
  print "    search <query>       Full text search for <query> in your notes tree."
  print "    list [-all]          List all titles in your notes tree. Optional flag -all prints full paths."
  print "    edit <title>         Open the note named <title> in $EDITOR."
  print ""
  print "    track                Log data for tracking."
  print ""
  print "    journal  [-e]        Create a new journal entry."
  print "    journal read         Open the journal file."
  print ""
  print "    stack                View the current micronote stack."
  print "    push <unote>         Push a micronote onto the active stack."
  print "    pop <idx>            Unset the micronote at position idx."
  print ""
  print "    git-init             (Re-)Initialize version control in your notes tree."
  print "    git-commit           Commit the current state of your notes tree to version control."
  print "    git-log              View your version control commit log in $PAGER."
  print "    git-status           See the status of your notes tree with respect to unversioned changes."
  print ""
  print "    help                 Display this help message and quit."
  print ""
  print " Optional arguments:"
  print "    -e                   Encrypt using AES-256 with a 256 bit key.  Valid for: new, journal."
  print "    -all                 Print full paths.  Valid for: list."
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
      del stack[-1]
      save_stack(notespath, stack)
    elif int(argv[2]) >= 0 and int(argv[2]) < len(stack):
      del stack[int(argv[2])]
      save_stack(notespath, stack)
    else:
      print "Error!"
  
  elif argv[1] == 'new':
    path = "%s/%s" % (notespath,time.strftime("%Y/%m/%d"))
    mkdir_p(path)
    if argv[2] == '-e':
      if ENCR:
        vim_encrypted_file("%s/%s.mdown" % (path, argv[3]), new = True)
      else:
        os.system("$EDITOR %s/%s.mdown" % (path, argv[3]))
    else:
      os.system("$EDITOR %s/%s.mdown" % (path, argv[2]))
  
  elif argv[1] == 'cat':
    (fname, encrypted) = find_note_by_name(argv[2])
    if fname is False:
      print "Error: Object by name %s not found." % argv[2]
    else:
      if encrypted:
        if ENCR:
          vim_encrypted_file(fname, command = 'less', edit = False)
        else:
          print "Error: Missing PyCrypto, but file is encrypted. Aborting."
      else:
        os.system("$PAGER %s" % fname)
  
  elif argv[1] == 'edit':
    (fname, encrypted) = find_note_by_name(argv[2])
    if fname is False:
      print "Error: Object by name %s not found." % argv[2]
    else:
      if encrypted:
        if ENCR:
          vim_encrypted_file(fname)
        else:
          print "Error: Missing PyCrypto, but file is encrypted. Aborting."
      else:
        os.system("$EDITOR %s" % fname)
  
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