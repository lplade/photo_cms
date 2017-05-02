import os
import uuid
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.postgres.fields import HStoreField
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
import exifread

# TODO import this from app settings
THUMBNAIL_SIZE = (200, 200)


def _gen_image_filename(instance, filename):
    """
    Generates a unique filename to store image.
    Also stores original filename.
    :param instance: instance of calling class
    :param filename: filename of uploaded object
    :return: Something like 'images/23/a5497075-c81d-499c-9aeb-326c4047dfe3.jpg'
    """
    # First, store the original filename in the model
    instance.original_filename = filename

    return _unique_path(instance.user.user.id, filename)


def _unique_path(user_id, filename, category='images'):
    """
    Generates a unique filename for storage
    :param category: 'images'
    :param user_id: instance.user.user.id
    :param filename: original filename
    :return: Something like 'images/23/a5497075-c81d-499c-9aeb-326c4047dfe3.jpg'
    """
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4(), ext)
    return os.path.join(category, user_id, filename)


def _gen_thumbs_filename(instance, filename):
    """
    Generates a path to store thumbnail.
    :param instance: instance of calling class
    :param filename: filename of 'uploaded' object
    :return: Something like 'thumbs/23/a5497075-c81d-499c-9aeb-326c4047dfe3_thumb.jpeg'
    """
    return os.path.join(
        'thumbs', instance.user.user.id, filename
    )


class Photo(models.Model):
    """
    Represents a single image including metadata
    """
    owner = models.ForeignKey('auth.User', blank=False)
    # We will use UUID as filename (36 chars)
    image_data = models.ImageField(
        upload_to=_gen_image_filename, max_length=36,
        width_field='width', height_field='height'
    )
    format = models.CharField(max_length=8)
    proxy_data = models.ImageField(  # "thumbnail"
        upload_to=_gen_thumbs_filename,
        max_length=36,
        null=True,
        blank=True
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
        # https://gist.github.com/valberg/2429288

        # make sure image data is set
        if not self.image_data:
            return False

        # Create a resized version of the image
        image = Image.open(self.image_data)
        image.thumbnail(THUMBNAIL_SIZE, Image.BICUBIC)

        # Save the thumbnail to in-memory 'file'
        temp_thumb = BytesIO()
        image.save(temp_thumb, 'jpeg')
        temp_thumb.seek(0)

        # Save image to a SimpleUploadFile which can be saved
        # into ImageField
        suf = SimpleUploadedFile(os.path.split(self.image_data.name)[-1],
                                 temp_thumb.read(), content_type='jpeg')
        thumb_filename = '{}_thumb.jpeg'.format(suf.name)

        # set save=False, or else it will infinite loop
        self.proxy_data.save(thumb_filename,
                             ContentFile(temp_thumb.read()),
                             save=False)
        temp_thumb.close()

        return True





