import os
import uuid
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.postgres.fields import HStoreField, ArrayField
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.core.files.storage import default_storage as storage
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO
import exifread
from django.utils.encoding import DjangoUnicodeDecodeError

from .validators import file_size


# TODO import this from app settings
THUMBNAIL_SIZE = (200, 200)

# List of exif tags to not store
# Includes binary and proprietary data
IGNORE_TAGS = ('GPSInfo', 'MakerNote', 'UserComment', 'ComponentsConfiguration')

# Override default User fields
User._meta.get_field('email')._unique = True
User._meta.get_field('email')._blank = False


# Helper functions #

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

    return _unique_path(instance.owner.pk, filename)


def _unique_path(user_id, filename, category='images'):
    """
    Generates a unique filename for storage
    :param category: 'images', could use for something else
    :param user_id: instance.user.user.id
    :param filename: original filename
    :return: Something like 'images/23/a5497075-c81d-499c-9aeb-326c4047dfe3.jpg'
    """
    ext = os.path.splitext(filename)[-1]
    new_filename = '{}{}'.format(uuid.uuid4(), ext)
    return os.path.join(category, str(user_id), new_filename)


def _gen_thumbs_filename(instance, filename):
    """
    Generates a path to store thumbnail.
    :param instance: calling Photo
    :param filename: filename of 'uploaded' object
    :return: Something like 'thumbs/23/a5497075-c81d-499c-9aeb-326c4047dfe3.jpeg'
    """
    return _unique_path(instance.owner.pk, filename, category='thumbs')


class FractionDict:
    """
    Simple class to store a fraction of integers
    """

    def __init__(self, numerator, denominator):
        """

        :param numerator: integer numerator
        :param denominator: integer denominator
        """
        self.numerator = int(numerator)
        self.denominator = int(denominator)

    def get_as_dict(self):
        """
        Returns the fraction as a dictionary {'numerator', 'denominator'}
        :return: Dictionary with keys 'numerator' and 'denominator'
        """
        return {'numerator': self.numerator,
                'denominator': self.denominator}

    def get_as_float(self):
        """
        Returns the mathematical value of the fraction
        :return: Float of numerator / denominator
        """
        return float(self.numerator / self.denominator)

    def set_by_dict(self, dictionary):
        """
        Stores numerator and denominator by dict with keys 'numerator' and 
        'denominator'
        :param dictionary: dict with keys 'numerator' and 'denominator'
        :return: True if no error
        """
        assert 'numerator' in dictionary and 'denominator' in dictionary
        self.numerator = int(dictionary['numerator'])
        self.denominator = int(dictionary['denominator'])
        return True

    def set_by_list(self, _list):
        """
        Store numerator and denominator by list [numerator, denominator]
        :param _list: list of [numerator, denominator]
        :return: True if no error
        """
        assert _list.length == 2
        self.numerator = int(_list[0])
        self.denominator = int(_list[1])
        return True

    def __repr__(self):
        return self.get_as_dict()

    def __str__(self):
        return '{}/{}'.format(self.numerator, self.denominator)


# Models #

class Profile(models.Model):
    """
    User profile
    """
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')
    display_name = models.CharField(max_length=64)
    about = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=127, blank=True)
    country = models.CharField(max_length=127, blank=True)

    def save(self, *args, **kwargs):
        # If display_name is not set, use username
        if self.display_name is None or self.display_name == '':
            self.display_name = self.user.username
        super(Profile, self).save(*args, **kwargs)

    def get_username(self):
        return self.user.username


class Gallery(models.Model):
    """
    This represents a collection of photos
    """
    owner = models.ForeignKey('auth.User', blank=False)
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    # ManyToManyField set in Photo
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'galleries'

    def __str__(self):
        photo_count = self.photos.count()
        return '{} ({} photos)'.format(self.name, photo_count)

    def save(self, *args, **kwargs):
        # Update modified time
        self.modified_datetime = timezone.now()
        super(Gallery, self).save(*args, **kwargs)


class Photo(models.Model):
    """
    Represents a single image including metadata
    """

    # Model improved with help from
    # https://djangosnippets.org/snippets/2094/

    owner = models.ForeignKey('auth.User', blank=False)
    # We will use UUID as filename (36 chars)
    image_data = models.ImageField(
        upload_to=_gen_image_filename,
        width_field='image_width', height_field='image_height',
        validators=[file_size]
    )
    # Should be auto-populated by ImageField
    image_height = models.IntegerField(blank=True, editable=False)
    image_width = models.IntegerField(blank=True, editable=False)

    format = models.CharField(max_length=8, blank=True, editable=False)

    proxy_data = models.ImageField(  # "thumbnail"
        upload_to=_gen_thumbs_filename,
        width_field='proxy_width', height_field='proxy_height',
        null=True,
        blank=True,
        editable=False
    )
    proxy_height = models.IntegerField(null=True, blank=True, editable=False)
    proxy_width = models.IntegerField(null=True, blank=True, editable=False)

    original_filename = models.TextField(blank=True)
    created_datetime = models.DateTimeField(default=timezone.now)
    modified_datetime = models.DateTimeField(default=timezone.now)

    # HStoreField is Postgres-specific, stores a dict
    # Needs to be enabled on Postgres side too
    # https://docs.djangoproject.com/en/1.11/ref/contrib/postgres/fields/#hstorefield
    exif_tags = HStoreField(blank=True)
    # TODO store tags in own table for querying

    # TODO GPS data (should be in exifread dict)
    # TODO XMP data?
    # TODO IPTC-IIM data?

    # List of galleries this photo is in
    galleries = models.ManyToManyField(Gallery,
                                       related_name='photos',
                                       blank=True)

    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return '{}@{}'.format(self.original_filename, self.image_data.name)

    def save(self, *args, **kwargs):

        # Update modified time
        self.modified_datetime = timezone.now()

        # Determine image format if not already set
        if self.format != self.get_format():
            self.format = self.get_format()

        # Read Exif tags from JPEG
        self.exif_tags = self.get_exif()

        # Generate a thumbnail
        # http://stackoverflow.com/a/43011898/7087237
        if not self.make_thumbnail():
            raise Exception('Could not create thumbnail')

        force_update = False
        # If it has already been saved, we can force update
        if self.id:
            force_update = True

        super(Photo, self).save(force_update=force_update, *args, **kwargs)

    def get_format(self):
        """
        Uses Pillow to determine image format
        :return: Pillow image format
        """
        image = Image.open(self.image_data)
        return image.format

    def get_exif(self):
        """
        Uses exifread to get Exif tags
        :return: dict of tags
        """
        _tags = {}
        image = Image.open(self.image_data)

        exif = image._getexif()
        if exif:
            for tag, value in exif.items():

                # Skip any tags we don't want
                if tag not in IGNORE_TAGS:
                    decoded = TAGS.get(tag, tag)
                    # Some cameras have non-Unicode Exif tags,
                    # so be sure to cast them or we crash
                    _tags[str(decoded)] = str(value)

        # Note: exifread provides better READING of Exif than Pillow,
        # but can't write any changes.
        # _exif_tags = exifread.process_file(self.image_data, details=False)
        # assert _exif_tags is not None

        return _tags

    def make_thumbnail(self):
        """
        Generates a thumbnail image with Pillow, and saves it as a proxy
        image in the model.
        :return: True if successful, False if no original image
        """
        # https://gist.github.com/valberg/2429288

        # make sure image data is set
        if not self.image_data:
            return False

        if self.proxy_data:
            return True

        # Create a resized version of the image
        image = Image.open(self.image_data)
        image.thumbnail(THUMBNAIL_SIZE, Image.BICUBIC)

        # Save the thumbnail to in-memory 'file'
        temp_thumb = BytesIO()
        image.save(temp_thumb, 'jpeg')
        temp_thumb.seek(0)  # rewinds the file

        # Save image to a SimpleUploadFile which can be saved
        # into ImageField
        # TODO figure out how to pass base image's UUID before
        # image is committed to DB
        basename = os.path.basename(self.image_data.name)
        uuidname = os.path.splitext(basename)[0]
        suf = SimpleUploadedFile(uuidname,
                                 temp_thumb.read(), content_type='image/jpeg')
        thumb_filename = '{}_thumb.jpeg'.format(suf.name)

        # set save=False, or else it will infinite loop
        self.proxy_data.save(thumb_filename,
                             suf,
                             save=False)

        # Also store the real dimensions for the Pillow thumbnail
        self.proxy_width, self.proxy_height = image.size

        temp_thumb.close()

        return True


# TODO finish implementing this
class ExifTag(models.Model):
    photo = models.OneToOneField(
        Photo,
        on_delete=models.CASCADE,
        related_name='exif'
    )
    # ISOSpeedRatings
    iso_speed_ratings = models.IntegerField
    # Make
    make = models.CharField(max_length=128, blank=True)
    # Model
    model = models.CharField(max_length=128, blank=True)
    # FNumber (n, d)
    _f_number = HStoreField(blank=True)
    # FocalLength (n, d)
    _focal_length = HStoreField(blank=True)
    # ExposureTime (n, d)
    _exposure_time = HStoreField(blank=True)
    # Copyright
    # Artist
    # UniqueCameraModel
    # Software
    # ImageLength
    # ImageWidth
    # XResolution
    # YResolution
    # DateTime
    # DateTimeOriginal
    # Orientation
    # DateTimeDigitized
    # FocalLengthIn35mmFilm
    # ExposureBiasValue

    def __str__(self):
        return "Exif data for {}".format(self.photo)

    # TODO subclass fraction from HStoreField or ArrayField

    # These methods behave as fields that map HStoreField to a FractionDict

    def f_number(self, numerator=None, denominator=None):
        # 'setter'
        if numerator and denominator:
            fraction = FractionDict(numerator, denominator)
            self._f_number = fraction.get_as_dict()

        # 'getter'
        else:
            if 'numerator' in self._f_number \
                    and 'denominator' in self._f_number:
                fraction = FractionDict(
                    self._f_number['numerator'],
                    self._f_number['denominator'])
            else:
                fraction = None
        return fraction

    def focal_length(self, numerator=None, denominator=None):
        # 'setter'
        if numerator and denominator:
            fraction = FractionDict(numerator, denominator)
            self._focal_length = fraction.get_as_dict()

        # 'getter'
        else:
            if 'numerator' in self._focal_length \
                    and 'denominator' in self._focal_length:
                fraction = FractionDict(
                    self._focal_length['numerator'],
                    self._focal_length['denominator'])
            else:
                fraction = None
        return fraction

    def exposure_time(self, numerator=None, denominator=None):
        # 'setter'
        if numerator and denominator:
            fraction = FractionDict(numerator, denominator)
            self._exposure_time = fraction.get_as_dict()

        # 'getter'
        else:
            if 'numerator' in self._exposure_time \
                    and 'denominator' in self._exposure_time:
                fraction = FractionDict(
                    self._exposure_time['numerator'],
                    self._exposure_time['denominator'])
            else:
                fraction = None
        return fraction

