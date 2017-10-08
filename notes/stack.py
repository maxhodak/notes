import json

def add_commands(subparsers):
    a = subparsers.add_parser('stack', help='View the current stack')
    a.set_defaults(func = _stack)
    a = subparsers.add_parser('push', help='Push an item onto the stack')
    a.add_argument('item', type=str)
    a.set_defaults(func = _push)
    a = subparsers.add_parser('pop', help='Pop an item from the stack')
    a.add_argument('-x', type=int)
    a.set_defaults(func = _pop)

def load_stack(args):
  try:
    return json.load(open("%s/.stack" % args.root, 'r+'))
  except ValueError:
    return []

def save_stack(args, stack = []):
  return json.dump(stack, open("%s/.stack" % args.root, 'w'))

def _stack(args):
    data = load_stack(args)
    for i in xrange(len(data)):
      print(" ==> [%i] %s" % (i, data[i]))

def _push(args):
    data = load_stack(args)
    data.append(args.item)
    save_stack(args, data)

def _pop(args):
    data = load_stack(args)
    if len(data) == 0:
      print("Stack empty, nothing to pop")
    elif args.x and args.x >= 0 and args.x < len(data):
      del data[args.x]
      save_stack(args, data)
    elif not args.x:
      print(" ==> %s" % (data[-1], ))
      del data[-1]
      save_stack(args, data)
    else:
      print("Bad index: %d (stack size = %d)" % (args.x, len(data)))
