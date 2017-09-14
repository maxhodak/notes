import os
from notes import fs

def add_commands(subparsers):
    a = subparsers.add_parser('git-init', help='Initialize version control in your notes tree.')
    a.set_defaults(func = _git_init)
    a = subparsers.add_parser('commit', help='Commit the current state of your notes tree to version control.')
    a.set_defaults(func = _commit)
    a = subparsers.add_parser('log', help='View your version control commit log in $PAGER.')
    a.set_defaults(func = _git_log)
    a = subparsers.add_parser('status', help='See the status of your notes tree with respect to unversioned changes.')
    a.set_defaults(func = _status)

def _git_init(args):
    fs.mkdir_p(notespath)
    os.system("echo '.DS_Store' > %s/.gitignore" % args.root)
    os.system("cd %s && git init ." % args.root)

def _git_log(args):
    os.system("cd %s && git log" % args.root)

def _status(args):
    os.system("cd %s && git status -uall" % args.root)

def _commit(args):
    os.system("cd %s && git status --porcelain -uall | grep '^??' | cut -d' ' -f2 | xargs git add" % args.root)
    os.system("cd %s && git commit -a" % (args.root, commit_msg))
