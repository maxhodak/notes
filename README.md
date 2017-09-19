# Notes

A highly hackable system for keeping notes that includes a lightweight command line-based task tracker and some advanced features like an Ethereum blockchain notary and git integration, all of which is encrypted by default and kept on your own file system. Notes uses whatever editor and pager you use normally, like vim or Atom and more or less.

Notes exists because the text flow I use for development works just as good for non-code as it does for code, which is to say, much better than a WYSIWYG editor; being able to easily extend and integrate my note management tooling with other stuff has been super useful over the years; and Evernote is eventually going to get hacked.

## Basic Use

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

Notes does not support multiple notes with same name on the same day.

To delete a note, just use `rm` on a regular command line. (There is no way to delete a file using notes.)

## Stack: miniature task tracking and reminders

Programmers often refer to having a mental stack.

    $ note stack

    ==> [0] Get correct answers for BME 153 homework
    ==> [1] Go running
    ==> [2] Negotiate seat to Mars

To add a new item:

    $ note push "Adding a new item!"

appends it.  To remove an item,

    $ note pop

removes the most-recently-inserted item. You can also specify a position:

    $ note pop -x 2

to remove the note at position 2 (see the numbers in brackets to the right of the arrows above?)

I usually define several shell aliases for this feature:

    alias push='notes push'
    alias pop='notes pop'
    alias peek='notes stack'

## Journal & Scratchpad

Notes has a first-class concepts for a few common idioms.

    $ notes scratch

Will open a persistent document to use as a scratch file.

    $ notes journal

Will put a `daily.mdown` file in the current day's directory. You can use a `--date` argument to specify a day other than today. This is equivalent to calling `notes new daily --date YYYY/MM/dd`

## Blockchain Notary

Notes can publish hashes of your content to the Ethereum blockchain as a form of secure proof-of-existence timestamping.  All hashes are calculated on the plaintext of your note content, not the encrypted resting contents of the files. To just see the SHA256 hash of a note without publishing anything:

    $ notes hash NoteTitle

To publish a hash to the Ethereum blockchain:

    $ notes notarize NoteTitle

In order to use this feature, you must be running an Ethereum client with an RPC server that exposes the eth, web3, and personal APIs, for example:

    $ geth --syncmode "light" --cache 1024 --rpcapi eth,web3,personal --rpc

It's a good idea to commit a checkpoint when you notarize a file so you can recover the state the hash corresponds to later, in case that note is edited further.

## Version Control

    notes git-init
    notes checkpoint
    notes log
    notes status
    notes version

## Encryption

All notes are encrypted as separate files. Importantly, as of now, titles are filenames and are themselves not encrypted. For details on what kind of encryption notes uses, see `notes/security.py`.

## Full Usage

(For my setup, where I'm using Atom and less.)

    $ notes -h

    usage: notes [-h] [--root -r]
                 {new,cat,list,edit,scratch,search,journal,stack,push,pop,key,git-init,checkpoint,log,status,version,hash,notarize,notarize_raw}
                 ...

    A system for keeping notes. Editor is atom --wait, pager is less.

    optional arguments:
      -h, --help            show this help message and exit
      --root -r             Path to notes root directory (default: /home/max/notes)

    Commands:
      {new,cat,list,edit,scratch,search,journal,stack,push,pop,key,git-init,checkpoint,log,status,version,hash,notarize,notarize_raw}
        new                 Create a new note named <title> and open it in $EDITOR
        cat                 Display the content of <title> in $PAGER
        list                List all titles in your notes tree
        edit                Open the note named <title> in $EDITOR
        scratch             Open the scratch pad
        search              Full text search for <query> in your notes tree
        journal             Create a new note with today's date as the title
        stack               View the current stack
        push                Push an item onto the stack
        pop                 Pop an item from the stack
        key                 Inspect the keyfile
        git-init            Initialize version control in your notes tree
        checkpoint          Commit the current state of your notes tree to version control
        log                 View your version control commit log in $PAGER
        status              See the status of your notes tree with respect to unversioned changes
        version             See the current commit hash
        hash                Calculate SHA256 of note plaintext
        notarize            Publish a SHA256 hash to the Ethereum blockchain as a proof-of-existence timestamp
        notarize_raw        Publish an arbitrary string to the Ethereum blockchain as a proof-of-existence timestamp

    Notes is maintained by Max Hodak <maxhodak@gmail.com>. Please report issues at http://github.com/maxhodak/notes/issues/.

## Other

Notes keeps your data in `$NOTESPATH/%Y/%m/%d/<name>.mdown`; if not set, `$NOTESPATH` defaults to either `/Users/<username>/Documents/Notes/` or `/home/<username>/notes`, depending on platform.  Notes also creates a symlink aliasing `note` to `notes`, so you can use either; some of the commands just feel more natural after 'note', singular.
