import os

def add_commands(subparsers):
    a = subparsers.add_parser('search', help='Full text search for <query> in your notes tree.')
    a.set_defaults(func = _search)

def _search(args):
    os.system("grep -ir '%s' %s*" % (args.query, args.root))
