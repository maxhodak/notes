import time
from notes import fs

def add_commands(subparsers):
    new_note = subparsers.add_parser('new', help='Create a new note named <title> and open it in $EDITOR.')
    cat = subparsers.add_parser('cat', help='Display the content of <title> in $PAGER.')
    search = subparsers.add_parser('search', help='Full text search for <query> in your notes tree.')
    list_notes = subparsers.add_parser('list', help='List all titles in your notes tree. Optional flag -a prints full paths.')
    edit = subparsers.add_parser('edit', help='Open the note named <title> in $EDITOR')

def _new(args):
    path = "%s/%s" % (args.root, time.strftime("%Y/%m/%d"))
    fs.mkdir_p(path)
    edit_note("%s/%s.mdown" % (path, args.title))
