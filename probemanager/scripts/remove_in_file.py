import argparse
import re


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pattern", help="pattern to remove")
    parser.add_argument("-f", "--file", help="file")
    args = parser.parse_args()
    with open(args.file, 'r') as f:
        replaced = re.sub(args.pattern, '', f.read())
        print(replaced)
    with open(args.file, 'w') as f:
        f.write(replaced)
    exit()
