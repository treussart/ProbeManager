from cryptography.fernet import Fernet
from django.utils.crypto import get_random_string
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dest", help="", default='/etc/')
    args = parser.parse_args()
    fernet_key = Fernet.generate_key()

    with open(args.dest + 'fernet_key.txt', 'w') as f:
        f.write(fernet_key.decode('utf8'))

    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(50, chars)

    with open(args.dest + 'secret_key.txt', 'w') as f:
        f.write(secret_key)
    exit()
