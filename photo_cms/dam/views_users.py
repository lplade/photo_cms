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


def user_profile(request, user_pk):
    user = User.objects.get(pk=user_pk)
    user_galleries = Gallery.objects.filter(owner=user.pk)

    return render(request, 'dam/users/user_profile.html',
                  {'user': user, 'galleries': user_galleries})


@login_required
@transaction.atomic
def my_user_profile(request):
    # If no Profile is associated with User, create a Profile for tha tUser
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = Profile(user=request.user)

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

        return render(request, 'dam/users/modify_user.html',
                      {'form': form,
                       'profile': profile})


@login_required
def modify_user(request):
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
            return render(request, 'dam/users/change_password.html',
                          {'form': form})
    else:
        form = UserModificationForm()
        return render(request, 'dam/users/change_password.html',
                      {'form': form})


@login_required
def photoroll(request, user_pk):
    pass


def register(request):
    """
    Allow users to register profiles using built-in Django model auth.user
    :param request: 
    :return: 
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(
                username=request.POST['username'],
                password=request.POST['password1']
            )
            login(request, user)
            return redirect('dam:homepage')
        else:
            message = 'Please check the data you entered'
            return render(request, 'registration/register.html',
                          {'form': form, 'message': message})
    else:
        form = UserRegistrationForm()
        return render(request, 'registration/register.html',
                      {'form': form})


def logout_message(request):
    """
    logout redirect
    :param request: 
    :return: 
    """
    return render(request, 'dam/users/logout_message.html')

