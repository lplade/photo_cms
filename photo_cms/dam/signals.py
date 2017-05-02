from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Photo


@receiver(post_delete, sender=Photo)
def remove_files_from_storage(sender, instance, using):
    instance.image_data.delete(save=False)
    instance.proxy_data.delete(save=False)


# TODO regenerate thumbnail if photo changes (pre-save Photo)
