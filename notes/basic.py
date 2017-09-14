import os
import time
from notes import fs, edit, security, search

def add_commands(subparsers):
  a = subparsers.add_parser('new', help='Create a new note named <title> and open it in $EDITOR.')
  a.add_argument('title', type=str)
  a.add_argument('--date', metavar='-d',
    type=str,
    default=time.strftime("%Y/%m/%d"),
    help='Date to file under (default: %s)' % time.strftime("%Y/%m/%d")
  )
  a.set_defaults(func = _new)

  a = subparsers.add_parser('cat', help='Display the content of <title> in $PAGER.')
  a.add_argument('title', type=str)
  a.set_defaults(func = _cat)

  a = subparsers.add_parser('list', help='List all titles in your notes tree. Optional flag -a prints full paths.')
  a.add_argument('--all', dest='all', action='store_true')
  a.set_defaults(func = _list, all = False)

  a = subparsers.add_parser('edit', help='Open the note named <title> in $EDITOR')
  a.add_argument('title', type=str)
  a.set_defaults(func = _edit)

  a = subparsers.add_parser('scratch', help='Open the scratch pad')
  a.set_defaults(func = _scratch)

def find_note_by_name(args, name):
  files = [x for x in search.list_files(args) if name in x]
  if len(files) > 1:
    print "Multiple matches for %s found:" % name
    print "  idx\t\tName"
    for ix in range(len(files)):
      print "   %d\t%s" % (ix, files[ix])
    print ""
    selection = raw_input("  Select an index: ")
    print ""
    return files[int(selection)]
  return files[0]

def _new(args):
  key = security.keyfile_read(args)
  path = "%s/%s" % (args.root, args.date)
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
  key = security.keyfile_read(args)
  filename = find_note_by_name(args, args.title)
  if filename is False:
    print "Error: Object by name %s not found." % args.title
    return
  edit.with_editor(filename, key)

def _cat(args):
  key = security.keyfile_read(args)
  filename = find_note_by_name(args, args.title)
  if filename is False:
    print "Error: Object by name %s not found." % argv[2]
    return
  edit.with_editor(filename, key, command = ['less'])
