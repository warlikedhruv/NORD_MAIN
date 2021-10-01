from django.core.exceptions import ValidationError

from django.conf import settings
def validate_file_size(value):
    filesize= value.size
    if filesize > settings.MAX_UPLOAD_SIZE:
        raise ValidationError("The maximum file size that can be uploaded is 20MB")
    else:
        return value