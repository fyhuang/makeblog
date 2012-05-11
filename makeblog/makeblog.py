import sys
import argparse

import update

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('command_arg')
    args = parser.parse_args()

    if args.command == 'update':
        config = update.load_config(args.command_arg)
        update.update_all(config)
    elif args.command == 'wpimport':
        import wpimport
        wpimport.main(args.command_arg)
    else:
        print("Unknown command " + args.command)
        sys.exit(1)

if __name__ == "__main__":
    main()
