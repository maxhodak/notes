import binascii
import requests
import getpass
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from web3 import Web3, HTTPProvider, IPCProvider

from notes import security, basic, edit

def add_commands(subparsers):
    a = subparsers.add_parser('hash', help='Calculate SHA256 of note plaintext')
    a.add_argument('note', type=str)
    a.set_defaults(func = _hash)

    a = subparsers.add_parser('notarize', help='Publish a SHA256 hash to the Ethereum blockchain as a proof-of-existence timestamp')
    a.add_argument('note', type=str)
    a.add_argument('--rpc', type=str, default = 'http://localhost:8545')
    a.set_defaults(func = _notarize)

def _hash(args, return_values = False):
    key = security.keyfile_read(args)
    filename = basic.find_note_by_name(args, args.note)

    if filename is False:
      print "Error: Object by name %s not found." % args.note
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
    check = raw_input("Publish to Ethereum mainnet? (yes/no) ")
    if "yes" != check:
        print("Aborting!")
        return
    try:
        print("Connecting to %s..." % (args.rpc))
        web3 = Web3(HTTPProvider(args.rpc))
        print("Getting accounts...")
        accounts = web3.eth.accounts
    except Exception as e:
        print("Couldn't connect to RPC!")
        print(str(e))
        return

    if 0 == len(accounts):
        print("No Ethereum accounts found!")
        return
    elif 1 == len(accounts):
        account = accounts[0]
    else:
        for ix in range(len(accounts)):
            print(" [%d] %s" % (ix, accounts[ix]))
        while True:
            ch = raw_input("Which account do you want to use? [0 - %d] " % (len(accounts) - 1, ))
            try:
                ch = int(ch)
                if ch > -1 and ch < len(accounts):
                    account = accounts[ch]
                    break
            except:
                continue
    password = getpass.getpass("Enter password to unlock %s: " % account)
    try:
        web3.personal.signAndSendTransaction({
            'to': account,
            'from': account,
            'data': "0x" + hash_data
        }, password)
    except Exception as e:
        print("Couldn't complete transaction!")
        print(str(e))
