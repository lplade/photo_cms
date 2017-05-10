from django.http import HttpResponseForbidden, HttpResponseRedirect, \
    HttpResponse
from .models import Photo, Gallery, Profile
from .forms import GalleryDetailForm, GalleryCreateForm, GalleryDeleteForm

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
def gallery_details(request, gallery_pk):
    # This basically works like a photoroll, but we can add elements
    gallery = Gallery.objects.get(pk=gallery_pk)
    photos = Photo.objects.filter(galleries=gallery)\
        .order_by('created_datetime')
    # TODO order by Exif date

    if request.method == 'POST':
        form = GalleryDetailForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Editable fields we need to update go here
            gallery.save()
    else:
        form = GalleryDetailForm()

    return render(request, 'dam/gallery_details.html',
                  {'form': form,
                   'gallery': gallery,
                   'photos': photos,
                   'title': SITE_TITLE})


@login_required
def gallery_create(request):

    if request.method == 'POST':
        form = GalleryCreateForm(request.POST)
        if form.is_valid():
            gallery = form.save(commit=False)
            # if required fields included
            gallery.owner = request.user
            gallery.created_datetime = timezone.now()
            gallery.save()
            return redirect('dam:gallery_details', gallery_pk=gallery.pk)
    else:
        form = GalleryCreateForm()
    return render(request, 'dam/gallery_create.html',
                  {'form': form, 'title': SITE_TITLE})


@login_required
def gallery_delete(request, gallery_pk):
    gallery_to_delete = get_object_or_404(Gallery, id=gallery_pk)
    # If we don't own that gallery, return HTTP 403 Unauthorized
    if gallery_to_delete.owner != request.user:
        return HttpResponse(status=403)
    if request.method == 'POST':
        form = GalleryDeleteForm(request.POST, instance=gallery_to_delete)
        if form.is_valid():
            gallery_to_delete.delete()
            return HttpResponseRedirect('/user/galleries')
    else:
        form = GalleryDeleteForm(instance=gallery_to_delete)
    return render(request, 'dam/gallery_delete.html',
                  {'form': form,
                   'gallery': gallery_to_delete,
                   'title': SITE_TITLE})