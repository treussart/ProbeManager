from django.forms import ModelForm, PasswordInput

from .models import Server


class ServerForm(ModelForm):
    class Meta:
        model = Server
        fields = (
                  'name', 'host', 'os', 'remote_user', 'remote_port', 'become', 'become_method', 'become_user',
                  'become_pass', 'ssh_private_key_file')
        widgets = {
            'become_pass': PasswordInput(),
        }
