import getpass

from web3 import Web3, HTTPProvider, IPCProvider

def publish(args, data):
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
