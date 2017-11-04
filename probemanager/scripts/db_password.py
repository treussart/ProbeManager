import argparse
from getpass import getpass
from cryptography.fernet import Fernet


def encrypt(plain_text, dest):
    with open(dest + 'fernet_key.txt') as f:
        FERNET_KEY = bytes(f.read().strip(), 'utf-8')
    fernet_key = Fernet(FERNET_KEY)
    return fernet_key.encrypt(plain_text.encode('utf-8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dest", help="", default='/etc/')
    args = parser.parse_args()
    password = getpass('Type the password for the database, followed by [ENTER]: ')
    password_encrypted = encrypt(password, args.dest)

    with open(args.dest + 'password_db.txt', 'w') as f:
        f.write(password_encrypted.decode('utf-8'))
    f.close()
    exit(password)
