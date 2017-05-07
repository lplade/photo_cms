from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Photo, Profile
import django.core.exceptions

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Photo)
def remove_files_from_storage(sender, instance, **kwargs):
    """
    Remove the image and its thumb from storage
    :param sender: ignored
    :param instance: Photo in question
    :return: 
    """
    logger.debug('Deleting images!')
    instance.image_data.delete(False)
    instance.proxy_data.delete(False)


# TODO regenerate thumbnail if photo changes (pre-save Photo)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    When a User is created, also create a Profile
    :param sender: ignored
    :param instance: the User in question
    :param created: flag set True only on new instances
    :param kwargs: ignored
    :return: 
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Whenever we save updates to User, also save updates to its Profile
    :param sender: ignored
    :param instance: the User in question
    :param kwargs: ignored
    :return:
    """
    try:
        instance.profile.save()
    except django.core.exceptions.ObjectDoesNotExist:
        pass
