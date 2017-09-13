import time
from notes import fs, edit, security

def add_commands(subparsers):
  a = subparsers.add_parser('journal', help="Create a new note with today's date as the title.")
  a.add_argument('--date', metavar='-d', type=str, help='Date to resume')
  a.set_defaults(func = _journal)

def _journal(args):
  key = security.keyfile_read(args)

  date = time.strftime("%Y/%m/%d")
  if args.date:
    date = args.date

  path = "%s/%s" % (args.root, date)
  fs.mkdir_p(path)

  edit.with_editor("%s/%s.mdown" % (path, "daily"), key)
