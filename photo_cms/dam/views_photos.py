# Mostly based on LMNOP
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse

from .models import Photo, Gallery, Profile
from .forms import PhotoDetailForm, PhotoUploadForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

# TODO get from global config file
SITE_TITLE = 'Photos'


@login_required
def photo_details(request, photo_pk):
    photo = Photo.objects.get(pk=photo_pk)
    return render(request, 'dam/photo_details.html',
                  {'photo': photo, 'title': SITE_TITLE})


# https://coderwall.com/p/bz0sng/simple-django-image-upload-to-model-imagefield
@login_required
def photo_upload(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid() and request.FILES:
            photo = Photo(owner=request.user, image_data=request.FILES['image'])
            photo.save()
            return HttpResponseRedirect('/')

    else:
        form = PhotoUploadForm()

    return render(request, 'dam/photo_upload.html',
                  {'form': form,
                   'title': SITE_TITLE})
