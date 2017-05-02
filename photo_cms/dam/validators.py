from django.core.exceptions import ValidationError

MAX_FILE_SIZE = 50 * 1024 * 1024


def file_size(value):
    if value.size > MAX_FILE_SIZE:
        raise ValidationError('File too large! Limit {} bytes'
                              .format(MAX_FILE_SIZE))
