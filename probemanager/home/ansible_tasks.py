import logging
from ansible.plugins.callback import CallbackBase
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from home.utils import decrypt
from django.conf import settings


logger = logging.getLogger(__name__)


class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_async_ok(self, result):
        if 'stdout' in result._result:
            self.host_ok[result._task.get_name()] = {'task': result._task.get_name(), 'host': result._host.get_name(), 'message': result._result['stdout']}
        else:
            self.host_ok[result._task.get_name()] = {'task': result._task.get_name(), 'host': result._host.get_name(), 'message': result._result}

    def v2_runner_on_async_failed(self, result):
        self.host_failed[result._task.get_name()] = {'task': result._task.get_name(), 'host': result._host.get_name(), 'message': result._result}

    def v2_runner_on_ok(self, result, *args, **kwargs):
        if 'stdout' in result._result:
            self.host_ok[result._task.get_name()] = {'task': result._task.get_name(), 'host': result._host.get_name(), 'message': result._result['stdout']}
        else:
            self.host_ok[result._task.get_name()] = {'task': result._task.get_name(), 'host': result._host.get_name(), 'message': result._result}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._task.get_name()] = {'task': result._task.get_name(), 'host': result._host.get_name(), 'message': result._result}

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._task.get_name()] = {'task': result._task.get_name(), 'host': result._host.get_name(), 'message': result._result}


def execute(server, tasks):
    host_list = [server.host]
    Options = namedtuple('Options',
                         ['connection',
                          'module_path',
                          'forks',
                          'remote_user',
                          'private_key_file',
                          'ssh_common_args',
                          'ssh_extra_args',
                          'sftp_extra_args',
                          'scp_extra_args',
                          'become',
                          'become_method',
                          'become_user',
                          'check',
                          'diff',
                          'verbosity',
                          'timeout'])
    variable_manager = VariableManager()
    loader = DataLoader()
    # if server.host == 'localhost' or server.host == '127.0.0.1':
    #     connection = 'local'
    # else:
    #     connection = 'ssh'
    if server.ansible_ssh_private_key_file:
        private_key_file = settings.MEDIA_ROOT + "/" + server.ansible_ssh_private_key_file.file.name
    else:
        private_key_file = None
    options = Options(connection='smart',
                      module_path='/usr/share/ansible',
                      forks=100,
                      remote_user=server.ansible_remote_user,
                      private_key_file=private_key_file,
                      ssh_common_args=None,
                      ssh_extra_args=None,
                      sftp_extra_args=None,
                      scp_extra_args=None,
                      become=server.ansible_become,
                      become_method=server.ansible_become_method,
                      become_user=server.ansible_become_user,
                      check=False,
                      diff=False,
                      verbosity=None,
                      timeout=10
                      )
    if server.ansible_become_pass:
        passwords = {'become_pass': decrypt(server.ansible_become_pass)}  # dict(vault_pass='secret')
    else:
        passwords = dict()
    # Instantiate our ResultCallback for handling results as they come in
    results_callback = ResultCallback()

    # create inventory and pass to var manager
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=host_list)
    variable_manager.set_inventory(inventory)

    # create play with tasks
    play_source = dict(
        name="Ansible Play",
        hosts=host_list,
        gather_facts='no',
        port=server.ansible_remote_port,
        tasks=tasks
    )
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # actually run it
    tqm = None
    response = dict()
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=results_callback,
        )
        result_nbr = tqm.run(play)
        if result_nbr == 0:
            if results_callback.host_ok:
                response = {'result': result_nbr, 'tasks': results_callback.host_ok}
            else:
                response = {'result': result_nbr, 'tasks': ''}
            logger.debug("OK *******" + str(response))
        elif result_nbr == 4:
            if results_callback.host_unreachable:
                response = {'result': result_nbr, 'tasks': results_callback.host_unreachable}
            else:
                response = {'result': result_nbr, 'tasks': ''}
            logger.error("FAILED *******" + str(response))
        else:
            if results_callback.host_failed:
                response = {'result': result_nbr, 'tasks': results_callback.host_failed}
            else:
                response = {'result': result_nbr, 'tasks': ''}
            logger.error("FAILED *******" + str(response))
    except Exception as e:
        response = {'result': 255, 'tasks': e.__str__()}
        logger.error("FAILED ******* " + e.__str__())
    finally:
        if tqm is not None:
            tqm.cleanup()
    return response
