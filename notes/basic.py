import os
import time
from notes import fs, edit, security

def add_commands(subparsers):
    new_note = subparsers.add_parser('new', help='Create a new note named <title> and open it in $EDITOR.')
    new_note.add_argument('title', type=str)
    new_note.set_defaults(func = _new)
    cat = subparsers.add_parser('cat', help='Display the content of <title> in $PAGER.')
    cat.set_defaults(func = _cat)
    list_notes = subparsers.add_parser('list', help='List all titles in your notes tree. Optional flag -a prints full paths.')
    list_notes.add_argument('--all', dest='all', action='store_true')
    list_notes.set_defaults(func = _list, all = False)
    edit = subparsers.add_parser('edit', help='Open the note named <title> in $EDITOR')
    edit.set_defaults(func = _edit)
    delete = subparsers.add_parser('delete', help='Delete a note by ID')
    delete.set_defaults(func = _delete)
    scratch = subparsers.add_parser('scratch', help='Open the scratch pad')
    scratch.set_defaults(func = _scratch)

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

def _new(args):
    key = security.keyfile_read(args)
    path = "%s/%s" % (args.root, time.strftime("%Y/%m/%d"))
    fs.mkdir_p(path)
    edit.with_editor("%s/%s.mdown" % (path, args.title), key)

def _scratch(args):
    key = security.keyfile_read(args)
    edit.with_editor("%s/.scratch.mdown" % (args.root,), key)

def _list(args):
    if args.all:
        os.system("find %s/2* -name '*.mdown'" % args.root)
    else:
        os.system("find %s/2* -name '*.mdown' | cut -d '/' -f 9 | cut -d '.' -f 1" % args.root)

def _edit(args):
    (fname, encrypted) = find_note_by_name(argv[2])
    if fname is False:
      print "Error: Object by name %s not found." % argv[2]
    else:
      if encrypted:
          edit.with_editor(fname)
      else:
        os.system("$EDITOR %s" % fname)

def _cat(args):
    (fname, encrypted) = find_note_by_name(argv[2])
    if fname is False:
      print "Error: Object by name %s not found." % argv[2]
    else:
      if encrypted:
          edit_note(fname, command = ['less'])
      else:
        os.system("$PAGER %s" % fname)

def _delete(args):
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
