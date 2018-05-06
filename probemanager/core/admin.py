import logging

from django.contrib import admin
from django.contrib import messages
from django_celery_beat.models import SolarSchedule, IntervalSchedule

from .forms import ServerForm
from .models import SshKey, Server, Job, Configuration

logger = logging.getLogger(__name__)


class ServerAdmin(admin.ModelAdmin):
    form = ServerForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.become:
            response = obj.test_become()
        else:
            response = obj.test()
        if response['status']:
            messages.add_message(request, messages.SUCCESS, "Connection to the server OK")
        else:
            messages.add_message(request, messages.ERROR, "Connection to the server Failed")


class JobAdmin(admin.ModelAdmin):
    list_filter = ('status', 'completed', 'probe')
    list_display = ('name', 'probe', 'status', 'created', 'completed', 'result')
    list_display_links = None

    class Media:
        js = (
            'core/js/reload.js',
        )

    def has_add_permission(self, request):
        return False


admin.site.register(SshKey)
admin.site.register(Server, ServerAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Configuration)

admin.site.unregister(SolarSchedule)
admin.site.unregister(IntervalSchedule)
