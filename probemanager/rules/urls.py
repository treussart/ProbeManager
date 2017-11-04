from django.conf.urls import url
from rules import views

app_name = 'rules'

urlpatterns = [
    url(r'^search$', views.search, name='search'),
]
