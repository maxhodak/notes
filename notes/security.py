import os
import sys
import json
import getpass
import base64

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from notes import fs

KEYFILE_ACTIVE = False

def add_commands(subparsers):
  k = subparsers.add_parser('key', help="Inspect the keyfile")
  k.set_defaults(func = _show_key)

def _show_key(args):
    key = keyfile_read(args)
    print "Key ok!"

def keyfile_new(args):
    global KEYFILE_ACTIVE

    password = getpass.getpass("Creating new keyfile. Password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        raise Exception("Passwords didn't match!")
    salt, key = encrypt(password, Fernet.generate_key())
    data = {
        "key": key,
        "salt": salt
    }
    keyfile_save(args, data)

    KEYFILE_ACTIVE = data

    return data

def keyfile_read(args):
  global KEYFILE_ACTIVE

  if KEYFILE_ACTIVE: # memoize so we don't keep asking for a password
    return KEYFILE_ACTIVE

  try:
    data = json.load(open("%s/.key" % args.root, 'r+'))
  except Exception:
    fs.touch("%s/.key" % args.root)
    return keyfile_new(args)
  password = getpass.getpass("Password: ")
  data['decrypt_key'] = decrypt(data['key'], data['salt'], password)

  KEYFILE_ACTIVE = data

  return data

def keyfile_save(args, data):
  return json.dump(data, open("%s/.key" % args.root, 'w'))

def in_place_decrypt(filename, key):
  with open(filename, 'r') as f:
    data = json.load(f)
    plaintext = decrypt(data['data'], data['salt'], key['decrypt_key'])
  with open(filename, 'w') as f:
    f.write(plaintext)

def in_place_encrypt(filename, key):
  with open(filename, 'r') as fd:
    salt, ciphertext = encrypt(key['decrypt_key'], fd.read())
  with open(filename, 'wb') as fd:
    json.dump({
      "salt": salt,
      "data": ciphertext
    }, fd)

def encrypt(password, text, is_password = True):
    if is_password:
        salt = base64.urlsafe_b64encode(os.urandom(16))
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=bytes(salt),
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
    else:
        key = password
    f = Fernet(key)
    return (salt, base64.urlsafe_b64encode(f.encrypt(bytes(text))))

def decrypt(ciphertext, salt, password, b64 = True):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes(salt),
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    try:
        if b64:
            data = f.decrypt(base64.urlsafe_b64decode(ciphertext.encode("ascii")))
        else:
            data = f.decrypt(ciphertext)
    except InvalidToken:
        print "Bad password!"
        sys.exit(1)
    return data
