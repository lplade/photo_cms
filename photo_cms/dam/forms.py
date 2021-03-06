# mostly based on LMNOP
from django import forms
from .models import Profile, Photo, Gallery
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError


# User/Profile #

class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'password1',
                  'password2')

    def clean_username(self):
        username = self.cleaned_data['username']

        if not username:
            raise ValidationError('Please enter a username')

        if User.objects.filter(username__icontains=username).exists():
            raise ValidationError('A user with that username already exists')

        return username

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise ValidationError('Please enter your first name')

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise ValidationError('Please enter your last name')

        return last_name

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError('Please enter an email address')

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                'A user with that email address already exists')

        return email

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user


class UserModificationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise ValidationError('Please enter your first name')

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise ValidationError('Please enter your last name')

        return last_name

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError('Please enter an email address')

        return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # TODO this does not seem to pass display_name
        fields = ('display_name', 'about', 'city', 'state', 'country')
        # TODO validate display_name to not blank


# Photo #

class PhotoUploadForm(forms.Form):
    image = forms.ImageField(
        label='Select an image'
    )


class PhotoDetailForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('caption', 'galleries')
        widgets = {
            # Make the caption field nice and big
            'caption': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
            'galleries': forms.CheckboxSelectMultiple,
        }

    # def __init__(self, *args, **kwargs):
    #     super(PhotoDetailForm, self).__init__(*args, **kwargs)
    #     self.fields['galleries'] = forms.ModelMultipleChoiceField(
    #         queryset=Gallery.objects.all(),
    #         to_field_name='name',
    #         # empty_label="Choose galleries"
    #     )


class PhotoDeleteForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ()


# Gallery #

class GalleryDetailForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ('name', 'description')


class GalleryCreateForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ('name', 'description')


class GalleryDeleteForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ()
