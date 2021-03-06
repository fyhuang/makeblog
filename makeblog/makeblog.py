import sys
import argparse
from datetime import datetime

import compileblog
import server
import config as cf
import utils

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('command_arg')
    args = parser.parse_args()

    if args.command == 'compile':
        config = cf.load_config(args.command_arg)
        compileblog.compile_all(config)

    elif args.command == 'wpimport':
        import wpimport
        wpimport.main(args.command_arg)

    elif args.command == 'refresh':
        config = cf.load_config(args.command_arg)

        import twitter
        twitter.refresh_tweets(config)

    elif args.command == 'newpost':
        title = args.command_arg
        slug = utils.title_to_slug(title)
        now = datetime.utcnow()
        fname = 'drafts/{}-{}.md'.format(now.strftime('%Y-%m-%d-%H-%M'), slug)
        with open(fname, 'w') as f:
            f.write('---\ntitle: "')
            f.write(title)
            f.write('"\n---\n')

        import subprocess
        subprocess.call(['open', fname])

    elif args.command == 'edit' or args.command == 'editpost':
        # TODO
        pass
    elif args.command == 'publish':
        # TODO
        pass


    elif args.command == 'serve':
        config = cf.load_config(args.command_arg)
        config.is_dynamic = True
        server.serve(config)

    else:
        print("Unknown command " + args.command)
        sys.exit(1)

if __name__ == "__main__":
    main()
