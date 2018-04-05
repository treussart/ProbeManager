import argparse
import re


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pattern", help="pattern to remove", default=[], type=str, action='append')
    parser.add_argument("-f", "--file", help="file")
    args = parser.parse_args()
    for pattern in args.pattern:
        with open(args.file, 'r') as f:
            replaced = re.sub(pattern, '', f.read())
        with open(args.file, 'w') as f:
            f.write(replaced)
    exit()
