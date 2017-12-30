# python probemanager/scripts/utilities.py -d /usr/local/share/ProbeManager/ -p
import argparse
import sys
from getpass import getpass
from cryptography.fernet import Fernet


def encrypt(plain_text, dest):
    with open(dest + 'fernet_key.txt') as f:
        FERNET_KEY = bytes(f.read().strip(), 'utf-8')
    fernet_key = Fernet(FERNET_KEY)
    return fernet_key.encrypt(plain_text.encode('utf-8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dest", help="destination", default='/usr/local/share/ProbeManager/')
    parser.add_argument("-p", "--password", help="password")
    args = parser.parse_args()
    password = getpass('Type the password for the database, followed by [ENTER]: ')
    password_encrypted = encrypt(args.password, args.dest)
    print("Password encrypted : " + password_encrypted)
    sys.exit(0)
