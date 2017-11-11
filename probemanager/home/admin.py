from django.contrib import admin
from home.models import SshKey, Server, Job
from home.forms import ServerForm
from home.utils import encrypt
from django.contrib import messages
import logging


logger = logging.getLogger(__name__)


class ServerAdmin(admin.ModelAdmin):
    form = ServerForm

    def save_model(self, request, obj, form, change):
        if obj.ansible_become_pass:
            obj.ansible_become_pass = encrypt(obj.ansible_become_pass)
        super().save_model(request, obj, form, change)
        response = obj.test_root()
        if response['result'] == 0:
            messages.add_message(request, messages.SUCCESS, "Connection to the server OK")
        else:
            messages.add_message(request, messages.ERROR, "Connection to the server Failed : " + str(response['message']))


class JobAdmin(admin.ModelAdmin):
    list_filter = ('status', 'completed', 'probe')
    list_display = ('name', 'probe', 'status', 'created' 'completed', 'result')
    list_display_links = None

    def has_add_permission(self, request):
        return False


admin.site.register(SshKey)
admin.site.register(Server, ServerAdmin)
admin.site.register(Job, JobAdmin)
