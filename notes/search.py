import os
from glob import glob

def add_commands(subparsers):
    a = subparsers.add_parser('search', help='Full text search for <query> in your notes tree')
    a.add_argument('query', type=str)
    a.set_defaults(func = _search)

def _search(args):
    os.system("grep -ir '%s' %s*" % (args.query, args.root))
    # list_files(args)

def list_files(args):
    return [
        y for x in os.walk(args.root)
          for y in glob(os.path.join(x[0], '*.mdown'))
    ]
