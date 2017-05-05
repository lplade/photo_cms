from django.conf.urls import url

from . import views, views_users

app_name = 'dam'

urlpatterns = [
    # Login/logout/signup view are in app-level urls.py

    # Home page #

    url(r'^$', views.index, name='index'),

    # User #

    url(
        r'^user/profile/(?P<user_k>\d+)/$',
        views_users.user_profile,
        name='user_profile'
    ),

    url(
        r'^user/profile/$',
        views_users.my_user_profile,
        name='my_user_profile'
    ),

    url(
        r'^user/modify_user/',
        views_users.modify_user,
        name='modify_user'
    ),

    url(
        r'^user/logout_message/',
        views_users.logout_message,
        name='logout_message'
    )
]
