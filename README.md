# Notes

## Basic Use: Keeping track of notes

A note is just a text file identified by a name.  To create a new note,

    $ notes new mynote

and your editor will open with a blank file.  Save will commit to disk in the right place.  Once you've created a note, you can re-open it with

    $ notes edit mynotename

Note that `edit` and `new` are two different things!  Under the hood, notes keep track of metadata like creation date and `new` will create a `new` file under the current day's directory.  If you have multiple notes with the same name from different days, you'll get a disambiguation prompt:

    Multiple matches for mynotename found:
      idx   Name
       0    /Users/maxhodak/Documents/Notes/2010/11/03/mynotename.mdown
       1    /Users/maxhodak/Documents/Notes/2010/11/28/mynotename.mdown

      Select an index:

Notes does not support multiple notes with same name on the same day.  To search your existing notes for a string:

    $ notes search "Some String"

You can also delete a note:

    $ notes delete mynotename

though make sure you're using the version control features properly unless you really want to lose data.

Finally, to get a list of all of your notes, you can use:

    $ notes list

the long form of the list command, `notes list -a` is especially useful for piping to other command that operate on your notefiles.

## Stack: miniature task tracking and reminders

Programmers often refer to having a mental stack.

    $ note stack

    ==> [0] Get correct answers for BME 153 homework
    ==> [1] Go running
    ==> [2] Send back to proposal for Widgets

To add a new item:

    $ note push Adding a new item!

appends it.  To remove an item,

    $ note pop

removes the most-recently-inserted item. You can also specify a position:

    $ note pop 2

to remove the note at position 2 (see the numbers in brackets to the right of the arrows above?)

## Version Control

    notes git-init
    notes git-add
    notes git-commit
    notes git-log
    notes git-status

## Full Usage

(For my setup, where I'm using Atom and less.)

    $ notes help

    Editor is atom, pager is less.

    Usage: notes [COMMAND]

    Valid commands:
     new <title>            Create a new note named <title> and open it in $EDITOR.
     cat <title>            Display the content of <title> in $PAGER.
     search <query>         Full text search for <query> in your notes tree.
     list [-a]              List all titles in your notes tree. Optional flag -a prints full paths.
     edit <title>           Open the note named <title> in $EDITOR.
     journal                Create a new note with today's date as the title.
     scratch                Open the scratch pad.

     stack                  View the current micronote stack.  Short form: s.
     push <unote>           Push a micronote onto the active stack.
     pop <idx>              Unset the micronote at position idx.

     git-init               (Re-)Initialize version control in your notes tree.
     git-commit             Commit the current state of your notes tree to version control.
     git-log                View your version control commit log in $PAGER.
     git-status             See the status of your notes tree with respect to unversioned changes.

     help                   Display this help message and quit.

    Optional arguments:
     -a                     Print full paths.  Valid for: list.

## Other

Keeps your notes in `$NOTESPATH/%Y/%m/%d/<name>.mdown`; if not set, `$NOTESPATH` defaults to either `/Users/&lt;username&gt;/Documents/Notes/` or `/home/&lt;username&gt;/notes`, depending on platform.  Notes also creates a symlink aliasing `note` to `notes`, so you can use either; some of the commands just feel more natural after 'note', singular.
