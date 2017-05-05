from django.conf.urls import url

from . import views, views_users

app_name = 'dam'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
