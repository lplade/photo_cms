import uuid
from django.db import models
from django.utils import timezone

# TODO make this user configurable
THUMBNAIL_SIZE = [200, 200]


class Photo(models.Model):
    """
    Represents a single image including metadata
    """
    # Generate RFC 4122 UUID for use as primary key
    # and also use for filename on storage
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('auth.User', blank=False)
    # We will use UUID as filename (36 chars)
    image_data = models.ImageField(
        upload_to='images', max_length=36,
        width_field='width', height_field='height'
    )
    proxy_data = models.ImageField(
        upload_to='thumbs', max_length=36, editable=False
    )
    original_filename = models.TextField
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(default=timezone.now)
    # Should be auto-populated by ImageField
    height = models.IntegerField
    width = models.IntegerField
    # TODO Exif data
    # TODO GPS data
    # TODO XMP data
    # TODO IPTC-IIM data

    # TODO generate thumbnail -> proxy_data function

    def save(self, *args, **kwargs):
        # http://stackoverflow.com/a/43011898/7087237
        if not self.make_thumbnail():
            raise Exception('Could not create thumbnail')
        super(Photo, self).save(*args, **kwargs)

    def make_thumbnail(self):
        from PIL import Image

        image = Image.open(self.image_data)
        


class ExifTag(models.Model):
    """
    This represents the set of Exif data for an image.
    One-to-one mapping, but not all Photos have ExifTags
    """

