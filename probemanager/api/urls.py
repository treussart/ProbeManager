from django.apps.registry import apps
from rest_framework import routers
from django.conf import settings
from api import views
import importlib
import os


router = routers.DefaultRouter()

router.register(r'admin/users', views.UserViewSet)
router.register(r'admin/groups', views.GroupViewSet)
router.register(r'rules/classtype', views.ClassTypeViewSet)

for app in apps.get_app_configs():
    path = settings.BASE_DIR + "/" + app.label + "/api/urls.py"
    if os.path.isfile(path):
        my_attr = getattr(importlib.import_module(app.label + ".api.urls"), 'urls_to_register')
        for url in my_attr:
            router.register(*url)

urlpatterns = list()
urlpatterns += router.urls
