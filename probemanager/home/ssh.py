import subprocess
from django.conf import settings
import logging
from home.utils import decrypt
import os


logger = logging.getLogger(__name__)


def execute(server, commands):
    result = dict()
    # commands is a dict {'name of command': command}
    for command_name, command in commands.items():
        if server.ansible_become:
            command = " echo '" + decrypt(server.ansible_become_pass).decode('utf-8') + \
                      "' | " + server.ansible_become_method + " -S " + \
                      command
        # echo "rootpass" | sudo -S
        command_ssh = 'ssh -o StrictHostKeyChecking=no -p ' + \
                      str(server.ansible_remote_port) + ' -i ' + \
                      settings.MEDIA_ROOT + "/" + \
                      server.ansible_ssh_private_key_file.file.name + ' ' + \
                      server.ansible_remote_user + '@' + \
                      server.host + ' "' + command + ' "'
        exitcode, output = subprocess.getstatusoutput(command_ssh)
        if exitcode != 0:
            raise Exception("Command Failed",
                            "Command: " + command_name +
                            " Exitcode: " + str(exitcode) +
                            " Message: " + str(output)
                            )
        else:
            result[command_name] = output
    return result


def execute_copy(server, src, dest, owner=None, group=None, mode=None):
    result = dict()
    command_scp = 'scp -o StrictHostKeyChecking=no -P ' + \
                  str(server.ansible_remote_port) + ' -i ' + \
                  settings.MEDIA_ROOT + "/" + \
                  server.ansible_ssh_private_key_file.file.name + ' ' + \
                  src + ' ' + \
                  server.ansible_remote_user + '@' + \
                  server.host + ':' + dest
    if server.ansible_become:
        command_scp = 'scp -o StrictHostKeyChecking=no -P ' + \
                      str(server.ansible_remote_port) + ' -i ' + \
                      settings.MEDIA_ROOT + "/" + \
                      server.ansible_ssh_private_key_file.file.name + ' ' + \
                      src + ' ' + \
                      server.ansible_remote_user + '@' + \
                      server.host + ':' + os.path.basename(dest)
        exitcode, output = subprocess.getstatusoutput(command_scp)
        if exitcode != 0:
            raise Exception("Command scp Failed",
                            " Exitcode: " + str(exitcode) +
                            " Message: " + str(output)
                            )
        else:
            result['copy'] = output
        commands = {"mv": "mv " + os.path.basename(dest) + " " + dest}
        result['mv'] = execute(server, commands)['mv']
    else:
        exitcode, output = subprocess.getstatusoutput(command_scp)
        if exitcode != 0:
            raise Exception("Command scp Failed",
                            " Exitcode: " + str(exitcode) +
                            " Message: " + str(output)
                            )
        else:
            result['copy'] = output
    return result
