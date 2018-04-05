import argparse
from getpass import getpass
from cryptography.fernet import Fernet


def encrypt(plain_text, dest):
    with open(dest + 'fernet_key.txt') as f:
        fernet_key_bytes = bytes(f.read().strip(), 'utf-8')
    fernet_key = Fernet(fernet_key_bytes)
    return fernet_key.encrypt(plain_text.encode('utf-8')).decode('utf-8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dest", help="", default='/etc/')
    args = parser.parse_args()
    password = getpass('Type the password for the database, followed by [ENTER]: ')
    password_encrypted = encrypt(password, args.dest)

    with open(args.dest + 'password_db.txt', 'w') as f:
        f.write(password_encrypted)
    exit(password)
