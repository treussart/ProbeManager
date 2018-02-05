from django.contrib import admin

from .models import ClassType


class SourceAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'suricata/js/add-link-reference.js',
        )


admin.site.register(ClassType)
