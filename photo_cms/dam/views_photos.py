# Mostly based on LMNOP
from django.db import transaction

from .models import Photo, Gallery, Profile
from .forms import UserRegistrationForm, UserProfileForm, UserModificationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

# TODO get from global config file
SITE_TITLE = 'Photos'


def photo_details(request, photo_pk):
    photo = Photo.objects.get(pk=photo_pk)
    return render(request, 'dam/photo_details.html',
                  {'photo': photo, 'title': SITE_TITLE})
