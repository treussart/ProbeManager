import argparse
import re


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--remove", help="pattern to remove", default=[], type=str, action='append')
    parser.add_argument("-r", "--replace", help="pattern to replace separated by : "
                                                "example= 'ProbeManager:ProbeManager/probemanager/checkcve'",
                        default=[], type=str, action='append')
    parser.add_argument("-f", "--file", help="file")
    args = parser.parse_args()
    for pattern in args.remove:
        with open(args.file, 'r') as f:
            replaced = re.sub(pattern, '', f.read())
        with open(args.file, 'w') as f:
            f.write(replaced)
    for pattern in args.replace:
        old, new = pattern.split(':')
        with open(args.file, 'r') as f:
            replaced = re.sub(old, new, f.read())
        with open(args.file, 'w') as f:
            f.write(replaced)
    exit()
