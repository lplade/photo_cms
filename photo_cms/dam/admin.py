from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Photo, Gallery, Profile, ExifTag

# Register your models here.
admin.site.register(Photo)
admin.site.register(Gallery)
admin.site.register(ExifTag)


# Put Profile details in User details
class ProfileInLine(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profiles'


# Override User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInLine, )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
