import subprocess
from django.conf import settings


def execute(probe, commands):
    result = dict()
    # commands is a dict {'name of command': command}
    for command_name, command in commands.items():
        command_ssh = 'ssh -o StrictHostKeyChecking=no -p ' + str(probe.server.ansible_remote_port) + ' -i ' + settings.MEDIA_ROOT + "/" + probe.server.ansible_ssh_private_key_file.file.name + ' ' + probe.server.ansible_remote_user + '@' + probe.server.host + ' "' + command + '"'
        exitcode, output = subprocess.getstatusoutput(command_ssh)
        if exitcode != 0:
            raise Exception("Command Failed", "Command: " + command_name + " Exitcode: " + str(exitcode) + " Message: " + str(output))
        else:
            result[command_name] = output
    return result
