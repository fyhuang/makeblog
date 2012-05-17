import sys
import argparse
from datetime import datetime

import update
import utils

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('command_arg')
    args = parser.parse_args()

    if args.command == 'compile':
        config = update.load_config(args.command_arg)
        update.update_all(config)
    elif args.command == 'wpimport':
        import wpimport
        wpimport.main(args.command_arg)
    elif args.command == 'refresh':
        config = update.load_config(args.command_arg)

        import twitter
        twitter.refresh_tweets(config)
    elif args.command == 'newpost':
        title = args.command_arg
        slug = utils.title_to_slug(title)
        now = datetime.utcnow()
        fname = 'posts/{}-{}.md'.format(now.strftime('%Y-%m-%d-%H-%M'), slug)
        with open(fname, 'w') as f:
            f.write('---\ntitle: "')
            f.write(title)
            f.write('"\n---\n')

        import subprocess
        subprocess.call(['open', fname])
    else:
        print("Unknown command " + args.command)
        sys.exit(1)

if __name__ == "__main__":
    main()
