#!/usr/local/cs/bin/python3
import argparse
import sys
import random
import string

def parse_args():
    parser = argparse.ArgumentParser(
        description='Shuffle input lines and write to standard output.',
        usage='%(prog)s [OPTION]... [FILE]\n'
              '  or:  %(prog)s [OPTION]... --echo "args list"\n'
              '\n'
              'Options:\n'
              '  -e, --echo              treat each ARG as an input line\n'
              '  -i, --input-range LO-HI specify an input range (e.g., 1-5)\n'
              '  -n, --head-count=COUNT output at most COUNT lines\n'
              '  -r, --repeat            allow output lines to be repeated\n'
              '      --help              display this help and exit\n'
    )
    parser.add_argument('-e', '--echo', nargs='+',
                        help='treat each ARG as an input line')
    parser.add_argument('-i', '--input-range',
                        help='treat each number LO through HI as an input line')
    parser.add_argument('-n', '--head-count', type=int,
                        help='output at most COUNT lines')
    parser.add_argument('-r', '--repeat', action='store_true',
                        help='output lines can be repeated')
    parser.add_argument('file', nargs='?', default='-',
                        help='input file (default: standard input)')
    
    args = parser.parse_args()
    
    # Validate mutual exclusivity of --echo and --input-range
    if args.echo and args.input_range:
        parser.error("options --echo and --input-range are mutually exclusive")
    
    return args

def read_input(args):
    lines = []
    if args.echo:
        lines = args.echo
    elif args.input_range:
        range_str = args.input_range
        if '-' not in range_str:
            sys.stderr.write(f"shuf: invalid input range: '{range_str}'\n")
            sys.exit(1)
        lo, hi = range_str.split('-', 1)
        try:
            lo = int(lo)
            hi = int(hi)
            if lo > hi:
                sys.stderr.write(f"shuf: invalid input range: '{range_str}'\n")
                sys.exit(1)
            lines = [str(i) for i in range(lo, hi + 1)]
        except ValueError:
            sys.stderr.write(f"shuf: invalid input range: '{range_str}'\n")
            sys.exit(1)
    else:
        # Read from file or standard input
        if args.file == '-':
            try:
                lines = [line.rstrip('\n') for line in sys.stdin]
            except Exception as e:
                sys.stderr.write(f"shuf: error reading standard input: {e}\n")
                sys.exit(1)
        else:
            try:
                with open(args.file, 'r') as f:
                    lines = [line.rstrip('\n') for line in f]
            except IOError as e:
                sys.stderr.write(f"shuf: cannot open '{args.file}': {e.strerror}\n")
                sys.exit(1)
    return lines

def shuffle_lines(lines, repeat, head_count):
    if not lines:
        return

    if repeat:
        if head_count is None:
            while True:
                print(random.choice(lines))
        else:
            for _ in range(head_count):
                print(random.choice(lines))
    else:
        shuffled = lines.copy()
        random.shuffle(shuffled)
        if head_count is not None:
            shuffled = shuffled[:head_count]
        for line in shuffled:
            print(line)

def main():
    args = parse_args()
    lines = read_input(args)
    shuffle_lines(lines, args.repeat, args.head_count)

if __name__ == '__main__':
    main()
