import getpass

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def keyfile_new():
    password = getpass.getpass("Creating new keyfile. Password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        raise Exception("Passwords didn't match!")
    salt, key = encrypt(password, Fernet.generate_key())
    data = {
        "key": key,
        "salt": salt
    }
    keyfile_save(notespath, data)
    return data

def keyfile_read(notespath):
  try:
    data = json.load(open("%s/.key" % notespath, 'r+'))
  except Exception:
    touch("%s/.key" % notespath)
    return keyfile_new()
  password = getpass.getpass("Password: ")
  data['decrypt_key'] = decrypt(data['key'], data['salt'], password)
  return data

def keyfile_save(notespath, data):
  return json.dump(data, open("%s/.key" % notespath, 'w'))

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

def decrypt(ciphertext, salt, password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes(salt),
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    return f.decrypt(base64.urlsafe_b64decode(ciphertext))
