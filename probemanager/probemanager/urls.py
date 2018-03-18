from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view
from django.apps.registry import apps
from core.models import Probe


schema_view = get_swagger_view(title='ProbeManager API', url='/')

urlpatterns_modules = list()
for app in apps.get_app_configs():
    for model in app.get_models():
        if issubclass(model, Probe):
            if app.verbose_name != "Core":
                urlpatterns_modules.append(url(r'^' + app.label + '/', include(app.label + '.urls')))

urlpatterns = [
    url(r'^api/v1/doc/$', schema_view),
    url(r'^api/v1/', include('api.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^select2/', include('select2.urls')),
    url(r'^rules/', include('rules.urls')),
    url(r'^', include('core.urls')),
]
urlpatterns += urlpatterns_modules
