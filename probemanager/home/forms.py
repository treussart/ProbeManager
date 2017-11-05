from home.models import Server
from django.forms import ModelForm, PasswordInput


class ServerForm(ModelForm):
    class Meta:
        model = Server
        fields = ('host', 'os', 'ansible_remote_user', 'ansible_remote_port', 'ansible_become', 'ansible_become_method', 'ansible_become_user', 'ansible_become_pass', 'ansible_ssh_private_key_file')
        widgets = {
            'ansible_become_pass': PasswordInput(),
        }
