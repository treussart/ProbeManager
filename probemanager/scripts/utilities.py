# sudo /usr/local/share/ProbeManager/venv/bin/python /usr/local/share/ProbeManager/probemanager/scripts/utilities.py
# -d /usr/local/share/ProbeManager/
# venv/bin/python probemanager/scripts/utilities.py -d ~/git/Probemanager/
import argparse
import sys
import os
from getpass import getpass
from cryptography.fernet import Fernet


def encrypt(plain_text, dest):
    if os.path.exists(dest + 'fernet_key.txt'):
        with open(dest + 'fernet_key.txt') as f:
            fernet_key_bytes = f.read().strip().encode('utf-8')
    else:
        from django.conf import settings
        fernet_key_bytes = settings.FERNET_KEY
    fernet_key = Fernet(fernet_key_bytes)
    return fernet_key.encrypt(plain_text.encode('utf-8')).decode('utf-8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dest", help="destination", default='/usr/local/share/ProbeManager/')
    args = parser.parse_args()
    password = getpass('Type the password, followed by [ENTER]: ')
    password_encrypted = encrypt(password, args.dest)
    print("Password encrypted : " + password_encrypted)
    sys.exit(0)
