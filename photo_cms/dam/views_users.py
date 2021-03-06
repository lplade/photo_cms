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


def user_profile(request, user_pk):
    """
    User profile page
    :param request: http request object
    :param user_pk: primary key of requested user
    :return: render profile page to any user
    """
    user = User.objects.get(pk=user_pk)
    user_galleries = Gallery.objects.filter(owner=user.pk)

    return render(request, 'dam/user_profile.html',
                  {'user': user,
                   'galleries': user_galleries,
                   'title': SITE_TITLE, })


@login_required
@transaction.atomic
def my_user_profile(request):
    """
    Shows profile details for currently logged in user
    :param request: http request object
    :return: render profile form or update details
    """
    # If no Profile is associated with User, create a Profile for that User
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = Profile(user=request.user, display_name=request.user.username)

    if request.method == 'POST':
        form = UserProfileForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            profile.display_name = data['display_name']
            profile.about = data['about']
            profile.city = data['city']
            profile.state = data['state']
            profile.country = data['country']
            profile.save()

        return render(request, 'dam/user_modify.html',
                      # TODO message about updated
                      {'form': form,
                       'profile': profile,
                       'title': SITE_TITLE, })
    else:
        # If display_name is blank, pre-populate with username
        if profile.display_name is None or profile.display_name == '':
            form = UserProfileForm(
                initial={'display_name': profile.user.username})
        else:
            form = UserProfileForm()

    return render(request, 'dam/user_modify.html',
                  {'form': form,
                   'profile': profile,
                   'title': SITE_TITLE, })


@login_required
def modify_user(request):
    """
    Edits core User data
    :param request: http request object
    :return: renders User detail form or updates
    """
    if request.method == 'POST':
        form = UserModificationForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.get(pk=request.user.id)
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.password = data['password1']
            user.save()

            return redirect('dam:index')

        else:
            return render(request, 'dam/user_change_password.html',
                          {'form': form,
                           'title': SITE_TITLE, })
    else:
        form = UserModificationForm()
        return render(request, 'dam/user_change_password.html',
                      {'form': form,
                       'title': SITE_TITLE, })


@login_required
def my_photoroll(request):
    """
    Shows all photos for current user
    :param request: http request object
    :return: render photoroll
    """
    user = request.user

    # Catch if Profile is not set up and prompt user to enter details
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        return redirect('dam:my_user_profile')

    photos = Photo.objects.filter(owner=request.user)\
        .order_by('created_datetime')[:100]  # TODO order by Exif created tag
    # TODO get the full list and use JS to limit # displayed

    return render(request, 'dam/user_photoroll.html', {
        'title': SITE_TITLE,
        'user': user,
        'profile': profile,
        'photos': photos
    })


@login_required
def my_galleries(request):
    """
    Shows all galleries for current user
    :param request: http request object
    :return: render gallery list
    """
    user = request.user
    profile = request.user.profile
    galleries = Gallery.objects.filter(owner=request.user)\
        .order_by('created_datetime')
    return render(request, 'dam/user_galleries.html', {
        'title': SITE_TITLE,
        'user': user,
        'profile': profile,
        'galleries': galleries
    })


def register(request):
    """
    Allow users to register profiles using built-in Django model auth.user
    :param request: http request object
    :return: render new user signup form or creates user
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=request.POST['username'],
                password=request.POST['password1']
            )
            login(request, user)
            return redirect('dam:homepage')
        else:
            message = 'Please check the data you entered'
            return render(request,
                          'dam/auth_register.html',
                          {'form': form, 'message': message,
                           'title': SITE_TITLE, })
    else:
        form = UserRegistrationForm()
        return render(request, 'dam/auth_register.html',
                      {'form': form, 'title': SITE_TITLE, })


def logout_message(request):
    """
    Shows confirmation of user logout
    :param request: http request object
    :return: render logout confirmation
    """
    return render(request, 'dam/auth_logout.html', {'title': SITE_TITLE})

