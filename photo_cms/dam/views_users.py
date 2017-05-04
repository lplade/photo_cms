# Mostly based on LMNOP
from django.db import transaction

from .models import Photo, Gallery
from .forms import UserRegistrationForm

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

