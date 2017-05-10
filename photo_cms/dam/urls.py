from django.conf.urls import url

from . import views, views_users, views_photos, views_galleries

app_name = 'dam'

urlpatterns = [
    # Login/logout/signup view are in app-level urls.py

    # Home page #

    url(r'^$', views.home, name='homepage'),

    # User #

    # Publicly accessible user profile
    url(
        r'^user/profile/(?P<user_pk>\d+)/$',
        views_users.user_profile,
        name='user_profile'
    ),

    # Edit Profile for logged in user
    url(
        r'^user/profile/$',
        views_users.my_user_profile,
        name='my_user_profile'
    ),

    # Edit User for logged in user
    url(
        r'^user/modify_user/',
        views_users.modify_user,
        name='modify_user'
    ),

    # Displayed after logging out
    url(
        r'^user/logout_message/',
        views_users.logout_message,
        name='logout_message'
    ),

    # Displays all the logged in user's photos
    url(
        r'^user/photoroll/$',
        views_users.my_photoroll,
        name='my_photoroll'
    ),

    # Displays all the logged in user's galleries
    url(
        r'^user/galleries/$',
        views_users.my_galleries,
        name='my_galleries'
    ),

    # Photo #

    url(
        r'^photo/(?P<photo_pk>\d+)/$',
        views_photos.photo_details,
        name='photo_details'
    ),

    url(
        r'^photo/upload/$',
        views_photos.photo_upload,
        name='photo_upload'
    ),

    url(
        r'^photo/delete/(?P<photo_pk>\d+)/$',
        views_photos.photo_delete,
        name='photo_delete'
    ),

    # Gallery #

    url(
        r'^gallery/(?P<gallery_pk>\d+)/$',
        views_galleries.gallery_details,
        name='gallery_details'
    ),

    url(
        r'^gallery/create/$',
        views_galleries.gallery_create,
        name='gallery_create'
    ),

    url(
        r'^gallery/delete/(?P<gallery_pk>\d+)/$',
        views_galleries.gallery_delete,
        name='gallery_delete'
    )
]
