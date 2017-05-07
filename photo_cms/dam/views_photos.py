# Mostly based on LMNOP
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseRedirect, \
    HttpResponse
from django.urls import reverse

from .models import Photo, Gallery, Profile
from .forms import PhotoDetailForm, PhotoUploadForm, PhotoDeleteForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash

from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

# TODO get from global config file
SITE_TITLE = 'Photos'


@login_required
def photo_details(request, photo_pk):
    photo = Photo.objects.get(pk=photo_pk)

    if request.method == 'POST':
        form = PhotoDetailForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            photo.caption = data['caption']
            # Any other editable fields will go here
            photo.save()
    else:
        form = PhotoDetailForm()

    return render(request, 'dam/photo_details.html',
                  {'form': form,
                   'photo': photo,
                   'title': SITE_TITLE})


# https://coderwall.com/p/bz0sng/simple-django-image-upload-to-model-imagefield
@login_required
def photo_upload(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid() and request.FILES:
            photo = Photo(owner=request.user, image_data=request.FILES['image'])
            photo.save()
            # TODO figure out how to redir to details without crashing
            return HttpResponseRedirect('/user/photoroll')

    else:
        form = PhotoUploadForm()

    return render(request, 'dam/photo_upload.html',
                  {'form': form,
                   'title': SITE_TITLE})


# http://stackoverflow.com/a/13644671/7087237
@login_required
def photo_delete(request, photo_pk):
    photo_to_delete = get_object_or_404(Photo, id=photo_pk)
    # If we don't own that photo, return HTTP 403 Unauthorized
    if photo_to_delete.owner != request.user:
        return HttpResponse(status=403)
    if request.method == 'POST':
        form = PhotoDeleteForm(request.POST, instance=photo_to_delete)
        if form.is_valid():
            photo_to_delete.delete()
            return HttpResponseRedirect('/user/photoroll')
    else:
        form = PhotoDeleteForm(instance=photo_to_delete)
    return render(request, 'dam/photo_delete.html',
                  {'form': form, 'photo': photo_to_delete,
                   'title': SITE_TITLE})
