import binascii
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from notes import security, basic, edit, blockchain

def add_commands(subparsers):
    a = subparsers.add_parser('hash', help='Calculate SHA256 of note plaintext')
    a.add_argument('note', type=str)
    a.set_defaults(func = _hash)

    a = subparsers.add_parser('notarize', help='Publish a SHA256 hash to the Ethereum blockchain as a proof-of-existence timestamp')
    a.add_argument('note', type=str)
    a.add_argument('--rpc', type=str, default = 'http://localhost:8545')
    a.set_defaults(func = _notarize)

    a = subparsers.add_parser('notarize_raw', help='Publish an arbitrary string to the Ethereum blockchain as a proof-of-existence timestamp')
    a.add_argument('data', type=str)
    a.add_argument('--rpc', type=str, default = 'http://localhost:8545')
    a.set_defaults(func = _notarize_raw)

def _hash(args, return_values = False):
    key = security.keyfile_read(args)
    filename = basic.find_note_by_name(args, args.note)

    if filename is False:
      print("Error: Object by name %s not found." % args.note)
      return

    hash_data = edit.with_function(filename, key, _calculate_hash)
    if not return_values:
        print(hash_data)
    return (hash_data, filename)

def _calculate_hash(data):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(bytes(data))
    raw_hash = digest.finalize()
    return binascii.hexlify(raw_hash)

def _notarize(args):
    hash_data, filename = _hash(args, True)
    print("Calculated SHA256 hash of '%s' for plaintext of file '%s'" % (hash_data, filename))
    blockchain.publish(args, hash_data)

def _notarize_raw(args):
    blockchain.publish(args, binascii.hexlify(bytes(args.data)))
