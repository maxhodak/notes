import os
import sys
import argparse

from notes import basic, search, stack, journal, security, version

def _description(argv = sys.argv):
  return "A system for keeping notes. Editor is %s, pager is %s." % (
    os.getenv('EDITOR'), os.getenv('PAGER')
  )

def _epilog():
  return "Notes is maintained by Max Hodak <maxhodak@gmail.com>.  Please report issues at http://github.com/maxhodak/notes/issues/."

def _get_default_root():
    notespath = os.getenv("NOTESPATH")
    if notespath is None:
      if sys.platform in ("darwin"):
        notespath = "/Users/%s/Documents/Notes" % os.getlogin()
      elif sys.platform in ("linux2"):
        notespath = "/home/%s/notes" % os.getlogin()
      else:
        print "Platform not recognized and $NOTESPATH not set.  Please set $NOTESPATH first."
        sys.exit(2)
      os.system("touch %s/.stack" % notespath)
      print "$NOTESPATH not set; using default of %s" % notespath
      print "You should add `export NOTESPATH=%s` (or otherwise) to your shell profile." % notespath
    return notespath

def main():
    notespath = _get_default_root()

    parser = argparse.ArgumentParser(
        description = _description(),
        epilog = _epilog(),
        formatter_class = lambda prog: argparse.HelpFormatter(prog, width = 124)
    )
    parser.add_argument('--root', metavar = '-r', type = str, default = notespath,
                        help="Path to notes root directory (default: %s)" % notespath)

    subparsers = parser.add_subparsers(title='Commands')

    basic.add_commands(subparsers)
    search.add_commands(subparsers)
    journal.add_commands(subparsers)
    stack.add_commands(subparsers)
    security.add_commands(subparsers)
    version.add_commands(subparsers)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
