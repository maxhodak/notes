import os
import subprocess
import json
from notes import fs
from notes.migrate import migrate
from notes.security import in_place_decrypt, in_place_encrypt

def with_editor(filename, key, command = ["atom", "--wait"]):
  file_exists = os.path.isfile(filename)

  fs.touch(filename)

  if file_exists is True: # else, leave as blank file (accomplished by fs.touch above)
    try:
        in_place_decrypt(filename, key)
    except:
        was_migrated = migrate(filename, key, leave_decrypted = True)
        if not was_migrated:
            print("File exists but could not be read!")
            return False

  subprocess.call(command + [filename])

  in_place_encrypt(filename, key)

  return True

def with_function(filename, key, function):
  file_exists = os.path.isfile(filename)

  fs.touch(filename)

  if file_exists is True: # else, leave as blank file (accomplished by fs.touch above)
    try:
        in_place_decrypt(filename, key)
    except:
        was_migrated = migrate(filename, key, leave_decrypted = True)
        if not was_migrated:
            print("File exists but could not be read!")
            return False

  data = None
  with open(filename, 'r') as fd:
      data = function(fd.read())

  in_place_encrypt(filename, key)

  return data
