import time
from notes import fs

def add_commands(subparsers):
    subparsers.add_parser('journal', help="Create a new note with today's date as the title.")

def execute(args):
    date = time.strftime("%Y/%m/%d")
    if args.date:
      date = args.date
    path = "%s/%s" % (args.root, date)
    fs.mkdir_p(path)
    edit_note("%s/%s.mdown" % (path, "daily"))
