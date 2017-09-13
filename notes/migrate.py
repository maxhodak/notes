import os
import getpass
import subprocess
import marshal

from notes import fs
from notes.security import decrypt, encrypt

def detect_is_oldstyle(filename):
    with open(filename, 'r') as f:
      try:
        data = marshal.load(f)
      except:
        return False
      return data.startswith("!ENC%")

def migrate(filename, key, leave_decrypted = False):
  if not detect_is_oldstyle(filename):
      return False

  if not os.path.isfile(filename):
      return False

  print("File uses old-style encryption and requires migration.")
  password = getpass.getpass("Old file-specific password: ")

  with open(filename, 'r') as f:
    data = marshal.load(f)
    plaintext = decrypt(data[21:], data[5:21], password, b64 = False)
    if not plaintext.startswith("$aes256$"):
      raise ValueError("Invalid encryption password!")

  with open(filename, 'w') as f:
    f.write(plaintext[8:])

  if not leave_decrypted:
    in_place_encrypt(filename, key)

  return True
