from django.conf import settings
import logging
from home.utils import decrypt
import os
import paramiko


logger = logging.getLogger(__name__)


def connection(server):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=server.host,
                   username=server.remote_user,
                   port=server.remote_port,
                   key_filename=settings.MEDIA_ROOT + "/" + server.ssh_private_key_file.file.name
                   )
    return client


def execute(server, commands, become=False):
    result = dict()
    # commands is a dict {'name of command': command}
    for command_name, command in commands.items():
        if become:
            if server.become:
                if server.become_pass is not None:
                    command = " echo '" + decrypt(server.become_pass).decode('utf-8') + \
                              "' | " + server.become_method + " -S " + \
                              command
                else:
                    command = server.become_method + " " + command
            else:
                raise Exception("Server cannot become", server.name)
        client = connection(server)
        stdin, stdout, stderr = client.exec_command(command)
        # stdin.write(decrypt(server.become_pass).decode('utf-8') + '\n')
        if stdout.channel.recv_exit_status() != 0:
            raise Exception("Command Failed",
                            "Command: " + command_name +
                            " Exitcode: " + str(stdout.channel.recv_exit_status()) +
                            " Message: " + stdout.read().decode('utf-8') +
                            " Error: " + str(stderr.readlines())
                            )
        else:
            result[command_name] = stdout.read().decode('utf-8').replace('\n', '')
            if result[command_name] == '':
                result[command_name] = 'OK'

        client.close()
    return result


def execute_copy(server, src, dest, put=True, become=False):
    result = dict()
    client = connection(server)
    ftp_client = client.open_sftp()
    try:
        if put:
            if become:
                if server.become:
                    ftp_client.put(src, os.path.basename(dest))
                else:
                    raise Exception("Server cannot become", server.name)
            else:
                ftp_client.put(src, dest)
        else:
            ftp_client.get(dest, src)
    except Exception as e:
        raise Exception("Command scp Failed",
                        " Message: " + e.__str__()
                        )
    result['copy'] = "OK"
    if become:
        if server.become:
            commands = {"mv": "mv " + os.path.basename(dest) + " " + dest}
            result['mv'] = execute(server, commands, become=True)
    ftp_client.close()
    client.close()
    return result
