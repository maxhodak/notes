import os
import sys
import argparse
from notes import basic, stack, journal

def main():
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

    parser = argparse.ArgumentParser(description='notes')
    parser.add_argument('--root', metavar='-r', type=str, default=notespath,
                        help='Path to notes root directory')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')

    scratch = subparsers.add_parser('scratch', help="Open the scratch pad.")

    basic.add_commands(subparsers)
    stack.add_commands(subparsers)
    journal.add_commands(subparsers)

    parser.parse_args()

if __name__ == '__main__':
    main()
