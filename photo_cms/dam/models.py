import os
import uuid
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.postgres.fields import HStoreField
from PIL import Image
from io import BytesIO
import exifread

# TODO import this from app settings
THUMBNAIL_SIZE = (200, 200)


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
        upload_to='images/', max_length=36,
        width_field='width', height_field='height'
    )
    format = models.CharField(max_length=8)
    proxy_data = models.ImageField(  # "thumbnail"
        upload_to='thumbs/', max_length=36, editable=False
    )
    original_filename = models.TextField()
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(default=timezone.now)

    # Should be auto-populated by ImageField
    height = models.IntegerField()
    width = models.IntegerField()

    # HStoreField is Postgres-specific, stores a dict
    # https://docs.djangoproject.com/en/1.11/ref/contrib/postgres/fields/#hstorefield
    exif_tags = HStoreField()

    # TODO GPS data (should be in exifread dict)
    # TODO XMP data?
    # TODO IPTC-IIM data?

    # TODO generate thumbnail -> proxy_data function

    def __str__(self):
        return '{}.{}'.format(self.original_filename, self.format.lower())

    def _gen_filename(self):


    def save(self, *args, **kwargs):
        """
        
        :param args: 
        :param kwargs: 
        :return: 
        """
        # Determine image format if not already set
        if self.format != self.get_format():
            self.format = self.get_format()

        # Read Exif tags from JPEG
        if self.exif_tags is None:
            self.exif_tags = self.get_exif()

        # Generate a thumbnail
        # http://stackoverflow.com/a/43011898/7087237
        if not self.make_thumbnail():
            raise Exception('Could not create thumbnail')

        super(Photo, self).save(*args, **kwargs)

    def get_format(self):
        """
        
        :return: 
        """
        image = Image.open(self.image_data)
        return image.format

    def get_exif(self):
        """
        
        :return: 
        """
        # Note: exifread provides better READING of Exif, but can't write
        # any changes.
        image = Image.open(self.image_data)
        _exif_tags = exifread.process_file(image)
        return _exif_tags

    def make_thumbnail(self):
        """
        
        :return: 
        """
        # make sure image data is set
        if not self.image_data:
            return False

        # Create a resized version of the image
        image = Image.open(self.image_data)
        image.thumbnail(THUMBNAIL_SIZE, Image.BICUBIC)

        # Save the thumbnail to in-memory 'file'
        temp_thumb = BytesIO()
        image.save(temp_thumb, 'JPEG')
        temp_thumb.seek(0)

        # set save=False, or else it will infinite loop
        thumb_filename = '{}.{}'.format(id, '.jpg')
        self.proxy_data.save(thumb_filename,
                             ContentFile(temp_thumb.read()),
                             save=False)
        temp_thumb.close()

        return True





