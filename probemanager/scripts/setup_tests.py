from jinja2 import Template
from home.utils import encrypt
import os
import sys
from getpass import getpass
from shutil import copyfile
from django.conf import settings


template_server_test = """
[
{
    "model": "home.sshkey",
    "pk": 1,
    "fields": {
        "name": "test",
        "file": "ssh_keys/{{ ansible_ssh_private_key_file }}"
    }
},
{
    "model": "home.server",
    "pk": 1,
    "fields": {
        "host": "{{ host }}",
        "os": 1,
        "ansible_remote_user": "{{ ansible_remote_user }}",
        "ansible_remote_port": {{ ansible_remote_port }},
        "ansible_become": {{ ansible_become }},
        "ansible_become_method": "{{ ansible_become_method }}",
        "ansible_become_user": "{{ ansible_remote_user }}",
        "ansible_become_pass": "{{ ansible_become_pass }}",
        "ansible_ssh_private_key_file": 1
    }
}
]
"""


def run():
    skip = input('Add datas Tests ? (y/N) ')
    if skip.lower() == 'n' or not skip:
        sys.exit(0)
    else:
        print("Server for tests")
        host = input('host : ')
        ansible_become = input('ansible_become : (true/false) ')
        ansible_become_method = input('ansible_become_method : ')
        ansible_become_pass = getpass('ansible_become_pass : ')
        ansible_remote_user = input('ansible_remote_user : ')
        ansible_remote_port = input('ansible_remote_port : (0-65535) ')
        ansible_ssh_private_key_file = input('ansible_ssh_private_key_file : (Absolute file path) ')
        ansible_ssh_private_key_file_basename = os.path.basename(ansible_ssh_private_key_file)
        ssh_dir = settings.BASE_DIR + '/ssh_keys/'
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir)
        try:
            copyfile(ansible_ssh_private_key_file, ssh_dir + ansible_ssh_private_key_file_basename)
            os.chmod(ssh_dir + ansible_ssh_private_key_file_basename, 0o600)
        except Exception as e:
            print("Error in the path of the file : " + e.__str__())
            sys.exit(1)

        t = Template(template_server_test)
        server_test = t.render(host=host,
                               ansible_become=ansible_become,
                               ansible_become_method=ansible_become_method,
                               ansible_become_pass=encrypt(ansible_become_pass).decode('utf-8'),
                               ansible_remote_user=ansible_remote_user,
                               ansible_remote_port=ansible_remote_port,
                               ansible_ssh_private_key_file=ansible_ssh_private_key_file_basename
                               )
        with open(settings.BASE_DIR + '/home/fixtures/test-home-server.json', 'w') as f:
            f.write(server_test)
        f.close()
        sys.exit(0)
