from jinja2 import Template
from core.utils import encrypt
import os
import sys
from getpass import getpass
from shutil import copyfile
from django.conf import settings


template_server_test = """
[
{
    "model": "core.sshkey",
    "pk": 1,
    "fields": {
        "name": "test",
        "file": "ssh_keys/{{ ssh_private_key_file }}"
    }
},
{
    "model": "core.server",
    "pk": 1,
    "fields": {
        "host": "{{ host }}",
        "os": 1,
        "remote_user": "{{ remote_user }}",
        "remote_port": {{ remote_port }},
        "become": {{ become }},
        "become_method": "{{ become_method }}",
        "become_user": "{{ remote_user }}",
        "become_pass": "{{ become_pass }}",
        "ssh_private_key_file": 1
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
        become = input('become : (true/false) ')
        become_method = input('become_method : ')
        become_pass = getpass('become_pass : ')
        remote_user = input('remote_user : ')
        remote_port = input('remote_port : (0-65535) ')
        ssh_private_key_file = input('ssh_private_key_file : (Absolute file path) ')
        ssh_private_key_file_basename = os.path.basename(ssh_private_key_file)
        ssh_dir = settings.BASE_DIR + '/ssh_keys/'
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir)
        try:
            copyfile(ssh_private_key_file, ssh_dir + ssh_private_key_file_basename)
            os.chmod(ssh_dir + ssh_private_key_file_basename, 0o600)
        except Exception as e:
            print("Error in the path of the file : " + str(e))
            sys.exit(1)

        t = Template(template_server_test)
        server_test = t.render(host=host,
                               become=become,
                               become_method=become_method,
                               become_pass=encrypt(become_pass).decode('utf-8'),
                               remote_user=remote_user,
                               remote_port=remote_port,
                               ssh_private_key_file=ssh_private_key_file_basename
                               )
        with open(settings.BASE_DIR + '/core/fixtures/test-core-server.json', 'w') as f:
            f.write(server_test)
        f.close()
        sys.exit(0)
