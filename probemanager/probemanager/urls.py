from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings


schema_view = get_swagger_view(title='ProbeManager API', url='/')

urlpatterns_modules = list()
for app in settings.SPECIFIC_APPS:
    urlpatterns_modules.append(url(r'^' + app + '/', include(app + '.urls')))

urlpatterns = [
    url(r'^api/v1/doc/$', schema_view),
    url(r'^api/v1/', include('api.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^select2/', include('select2.urls')),
    url(r'^rules/', include('rules.urls')),
    url(r'^', include('core.urls')),
]
urlpatterns += urlpatterns_modules
